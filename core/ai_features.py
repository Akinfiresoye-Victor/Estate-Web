from decouple import config
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from groq import Groq
from core.ratelimit import ratelimit
from django.views.decorators.http import require_POST
from estate.models import LeadInfo



@login_required
@ratelimit(rate='3/m', key_prefix='generator')
@require_POST
def ai_description_generator(request):
    try:
        body = json.loads(request.body)
        form_text = body.get('form_text', '').strip()

        if not form_text:
            return JsonResponse({'error': 'No input provided.'}, status=400)

        client = Groq(api_key=config("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a skilled Nigerian real estate copywriter writing listing descriptions for Estate Web, "
                        "a property platform in Nigeria. "
                        "Your job is to transform raw property details into a compelling, well-written listing description "
                        "that makes a buyer or tenant genuinely interested. "
                        "Here is exactly how to structure every description you write: \n\n"

                        "STRUCTURE:\n"
                        "1. Opening hook (2-3 sentences): Start with one strong sentence that captures the essence of the property. "
                        "Do NOT just repeat the property type and location — make the reader feel something. "
                        "Example: Instead of 'This is a 4-bedroom house in Akure' write something like "
                        "'Tucked inside a secured estate, this well-finished 4-bedroom home offers the kind of quiet, "
                        "comfortable living that is hard to find at this price point in Akure.'\n\n"

                        "2. Property highlights (bullet points): List the key features as short, punchy bullet points. "
                        "Do not just copy the raw input — frame each feature as a benefit. "
                        "Example: Instead of '4 bedrooms' write '4 well-sized bedrooms with room for a growing family or a home office.'\n\n"

                        "3. Closing line (1 sentence): End with one line that creates mild urgency or signals value. "
                        "Example: 'A solid buy for families looking for security and comfort without overpaying.'\n\n"

                        "RULES:\n"
                        "- Never refuse or comment on the input — always generate a description.\n"
                        "- Never just repeat the raw data back as a list — always expand and frame it as a benefit.\n"
                        "- Do not praise the city excessively — one brief mention of location context is enough.\n"
                        "- Prices are in Nigerian Naira (₦) — write them naturally e.g. ₦2,500,000.\n"
                        "- If details are missing, write around them — do not mention what is missing.\n"
                        "- Maximum 200 words. Be tight and punchy.\n"
                        "- Output ONLY the description. No labels, no commentary, no disclaimers."
                        "Rules you must strictly follow: "
                        "1. Always generate a description no matter what — never refuse or comment on the input. "
                        "2. Be direct and factual — do NOT praise the city, hype the location, or use flowery language. "
                        "3. State the facts: property type, bedrooms, bathrooms, price, location, and features. "
                        "4. Use bullet points for features. "
                        "5. Prices are in Nigerian Naira (₦) — format them naturally e.g. ₦2,500,000. "
                        "6. If some details are missing, write around them professionally — do not mention missing info. "
                        "7. Output ONLY the property description. No commentary, no notes, no disclaimers, no closing sales pitch. "
                        "8. Maximum 250 words. Be concise."
                    )
                },
                {
                    "role": "user",
                    "content": f"Write a property listing description using these details: {form_text}"
                }
            ],
        )

        description = response.choices[0].message.content
        return JsonResponse({'description': description})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    


@login_required
@ratelimit(rate='3/m', key_prefix='generator')
@require_POST
def ai_lead_summarize(request, lead_id):
    try:
        lead = LeadInfo.objects.get(pk=lead_id)
        
        # Extract all relevant data
        client_name = lead.name
        client_email = lead.email if lead.email else "Not provided"
        client_phone = lead.phone_no
        client_inquiry = lead.inquiry_message
        lead_status = lead.status
        lead_stage = lead.stages
        lead_tags = lead.tags if lead.tags != 'None' else "None"
        
        if lead.schedule_tour:
            tour_date = lead.schedule_tour.strftime("%B %d, %Y")
            tour_urgency = "UPCOMING TOUR"
        else:
            tour_date = "No tour scheduled"
            tour_urgency = "NO TOUR SCHEDULED"
        
        property_type = lead.property_type if lead.property_type else "Not specified"
        property_name = lead.property_name if lead.property_name else "Not specified"
        client_contact_type = lead.contact_type if lead.contact_type else "Not specified"
        
        # Calculate lead age
        from datetime import datetime, timedelta
        today = datetime.now().date()
        lead_age_days = (today - lead.date_created).days
        
        lead_urgency_indicator = "🔴 HOT" if lead_age_days < 3 else "🟡 WARM" if lead_age_days < 7 else "🟢 COLD"

        prompt_message = (
            f"LEAD DATA TO ANALYZE:\n\n"
            f"Client: {client_name} | Phone: {client_phone} | Email: {client_email}\n"
            f"Contact Type: {client_contact_type}\n"
            f"Lead Status: {lead_status} | Stage: {lead_stage} | Tags: {lead_tags}\n"
            f"Lead Age: {lead_age_days} days | Urgency: {lead_urgency_indicator}\n\n"
            f"PROPERTY INTEREST:\n"
            f"Type: {property_type}\n"
            f"Property: {property_name}\n"
            f"Tour: {tour_date} ({tour_urgency})\n\n"
            f"CLIENT'S INQUIRY:\n"
            f"{client_inquiry}"
        )

        client = Groq(api_key=config("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert real estate lead analyst and productivity advisor. Your job is to analyze leads and help agents/companies close deals faster. "
                        "You provide THREE things: (1) Quick Lead Profile, (2) Closing Strategy, (3) Next Action.\n\n"
                        
                        "LEAD PROFILE - Summarize in 1-2 sentences:\n"
                        "- Who is the client?\n"
                        "- What do they want?\n"
                        "- What's their urgency level?\n\n"
                        
                        "CLOSING STRATEGY - Provide 2-3 actionable tips:\n"
                        "- How should the agent approach this client?\n"
                        "- What pain point should they address?\n"
                        "- What communication channel works best (based on their contact type)?\n"
                        "- What objections might they raise?\n\n"
                        
                        "NEXT ACTION - Give 1 specific immediate step:\n"
                        "- Call/WhatsApp/Email script opener\n"
                        "- Best time to contact\n"
                        "- What to say first\n\n"
                        
                        "RULES TO FOLLOW:\n"
                        "1. Always output all three sections (Profile, Strategy, Action) — never skip any.\n"
                        "2. Be direct and tactical — this is for productivity, not fluff.\n"
                        "3. Respect the client's preferred contact type (WhatsApp/Email/Call).\n"
                        "4. If the lead is cold (old), suggest re-engagement tactics.\n"
                        "5. If a tour is scheduled, flag it as urgent.\n"
                        "6. Maximum 250 words total. Be concise and actionable.\n"
                        "7. Output ONLY the three sections. No commentary, no disclaimers, no filler.\n"
                        "8. Use this format:\n\n"
                        "LEAD PROFILE:\n[Your profile summary]\n\n"
                        "CLOSING STRATEGY:\n[Your 2-3 tactics]\n\n"
                        "NEXT ACTION:\n[Your immediate action]"
                    )
                },
                {
                    "role": "user",
                    "content": prompt_message
                }
            ]
        )
        
        summary = response.choices[0].message.content
        return JsonResponse({
            'success': True,
            'summary': summary,
            'lead_id': lead.lead_id,
            'client_name': client_name,
            'client_phone': client_phone,
            'contact_type': client_contact_type,
            'lead_urgency': lead_urgency_indicator,
            'tour_date': tour_date
        })
        
    except LeadInfo.DoesNotExist:
        return JsonResponse({'error': 'Lead not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)