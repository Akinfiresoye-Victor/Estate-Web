from django.shortcuts import render, redirect
from datetime import date
from estate.models import *
from core.models import *
from decouple import config
from django.contrib import messages
from datetime import datetime, date
from django.conf import settings
from django.utils import timezone
from members.views import logout_user

User=settings.AUTH_USER_MODEL
# Create your views here.
'''Analytics For admin'''

admin= config('ADMIN')

#Total Listings and sign uo
def admin_dashboard(request):
    if request.user.username == admin:
        
        '''Property Tracking'''
        on_lease=PropertyManagementRent.objects.all()
        on_sale= PropertyManagementSale.objects.all()
        
        # Listings Calculation
        x_initial=PropertyManagementRent.objects.count() #where x is property on lease
        y_initial=PropertyManagementSale.objects.count() #where y is property on lease

        prop_calc=property_tracking(on_lease, on_sale, x_initial, y_initial)
        user_track=user_tracking()
        
        #properties calc
        total_listings=prop_calc[0]
        total_perc=prop_calc[1]
        percentage_rent= prop_calc[2]
        percentage_sale=prop_calc[3]
        final_rent_time= prop_calc[4]
        final_sale_time=prop_calc[5]
        final_update_time= prop_calc[6]
        todays_property=prop_calc[7]
        
        '''User Tranking'''
        user_count=user_track[0]
        user_increase_percentage= user_track[1]
        daily_active_users= user_track[2]
        final_time=user_track[3]

        
        context = {'users':user_count,
                    'users_inc_perc': user_increase_percentage,
                    'dau':daily_active_users,
                    'user_reg_time':final_time,
                    'on_lease_count': x_initial,
                    'on_sale_count':y_initial,
                    'total_listings': total_listings,
                    'rent_perc': percentage_rent,
                    'sale_perc': percentage_sale,
                    'total_perc': total_perc,
                    'rent_time':final_rent_time,
                    'sale_time':final_sale_time,
                    'final_update_time': final_update_time,
                    'today_property':todays_property}
        return render(request, 'admin_dashboard.html',context)
        


def property_tracking(on_lease, on_sale, x_initial, y_initial):
        
        x=0
        x_prev=0
        y=0
        y_prev=0
        
        '''Property count '''
        for prop in on_lease:
            if prop.listed_date.date() == date.today():
                x+=1
            else:
                x_prev += 1
        
        for prop in on_sale:
            if prop.listed_date.date() == date.today():
                y+=1
            else:
                y_prev += 1
        initial_time_listed_r=PropertyManagementRent.objects.order_by('-listed_date').first()
        initial_time_listed_s=PropertyManagementSale.objects.order_by('-listed_date').first()
        
        "Recent history"
        raw_rent_time=timezone.now() - initial_time_listed_r.listed_date
        formatted_rent_time=abs(raw_rent_time.total_seconds() / 60)
        final_rent_time=time_formatting(formatted_rent_time)
        
        raw_sale_time=abs(timezone.now() - initial_time_listed_s.listed_date)
        formatted_sale_time=raw_sale_time.total_seconds() / 60
        final_sale_time=time_formatting(formatted_sale_time)
        
        
        raw_rent_update_time= timezone.now() - initial_time_listed_r.last_updated
        formatted_rent_update_time=abs(raw_rent_update_time.total_seconds() / 60)
        final_rent_update_time=time_formatting(formatted_rent_update_time)
        
        raw_sale_update_time= timezone.now() - initial_time_listed_s.last_updated
        formatted_sale_update_time=abs(raw_sale_update_time.total_seconds() / 60)
        
        if formatted_sale_update_time > formatted_rent_update_time:
            formatted_update_time=formatted_sale_update_time
        elif formatted_sale_update_time < formatted_rent_update_time:
            formatted_update_time=formatted_rent_update_time
        else:
            formatted_update_time= (formatted_rent_update_time + formatted_sale_update_time) /2
        final_update_time= time_formatting(formatted_update_time)
        
        percentage_sale= (y/y_prev) * 100
        percentage_rent= (x/x_prev) * 100   
        
        total_perc= percentage_rent + percentage_sale
        total_listings= x_initial + y_initial
        
        property_listed_today=x + y
        
        calculated_percentages_list= [total_listings, total_perc, percentage_rent, percentage_sale, final_rent_time,
                                    final_sale_time, final_update_time, property_listed_today]
        return calculated_percentages_list

def user_tracking():
    user=User.objects.all()
    user_count=User.objects.count()
    
    
    users_today=0
    prev_users=0
    for users in user:
        if users.date_joined.date() == date.today():
            users_today += 1
        else:
            prev_users += 1
            
            
    daily_active_users=0
    for users in user:
        if users.last_login.date() == date.today():
            daily_active_users += 1
    
    user_increase_percentage= (users_today / prev_users) * 100
    
    
    
    # "%Y-%m-%d %H:%M:%S"
    lates_user=User.objects.order_by('-date_joined').first()
    user_reg_time= timezone.now() - lates_user.date_joined
    formatted_time=user_reg_time.total_seconds()/60
    final_time=time_formatting(formatted_time)
    user_tracking_list= [user_count,user_increase_percentage, daily_active_users, final_time]
    return user_tracking_list



def time_formatting(formatted_time):
    if formatted_time >= 60 and formatted_time <= 1439:
        formatted_time/=60
        if formatted_time == 1:
            final_time=f'{int(formatted_time)} Hours ago'
        else:
            final_time=f'{int(formatted_time)} Hours ago'
    elif formatted_time >= 1440:
        formatted_time/=1400
        if formatted_time == 1:
            final_time=f'{int(formatted_time)} Day Ago'
        else:
            final_time=f'{int(formatted_time)} Days Ago'
        
    else:
        if formatted_time <= 1:
            final_time=f'{int(formatted_time)} minute ago'
        else:
            final_time=f'{int(formatted_time)} minutes ago'
    return final_time





#for admins only
def view_feedbacks(request):
    # is_staff is Django's built-in flag for admin users.
    # It's safer than checking username == 'admin' because:
    # 1. Your admin username could change
    # 2. Another user could theoretically be named 'admin'
    # 3. is_staff works with Django's permission system properly
    print(request.user.id)
    if not request.user.is_staff:
        messages.warning(request, 'This page is for admins only.')
        return redirect('landing')

    feedbacks = Feedbacks.objects.all().order_by('-submitted_at')

    # ── Stats for the 4 stat boxes at the top of the page ────────────
    # These are simple database counts — Django does them in one query each.
    bug_count     = feedbacks.filter(category='bug').count()
    feature_count = feedbacks.filter(category='feature').count()

    # Average reaction score — only from submissions that have a reaction.
    # We exclude nulls (old records) so they don't drag the average down.
    from django.db.models import Avg
    avg_result = feedbacks.exclude(reaction__isnull=True).aggregate(Avg('reaction'))
    avg_raw    = avg_result['reaction__avg']

    # Round to 1 decimal place and show emoji next to it.
    # If no reactions yet, show a dash instead of crashing.
    if avg_raw is not None:
        avg_reaction = f"{avg_raw:.1f} ⭐"
    else:
        avg_reaction = "—"

    return render(request, 'view_feedback.html', {
        'feedback':      feedbacks,
        'bug_count':     bug_count,
        'feature_count': feature_count,
        'avg_reaction':  avg_reaction,
    })

#for admins only
def delete_feedback(request, feedback_id):
    if request.user.is_authenticated:
        if request.user.username == admin:
            #getting the property_id which will be used to handle the deletion
            feedback= Feedbacks.objects.get(pk=feedback_id)
            #keeps another user from deleting a users data 
            if request.user.id == 1:
                #what does the actual deleting based on the property_id
                feedback.delete()
                messages.success(request, ("Feedback deleted successfully"))
                return redirect('view-feedbacks')
            else:
                messages.error(request, ('You Arent authorized to delete this feedback'))
                return redirect('all-listings')
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('customers_url:landing')



def all_properties(request):
    if request.user.is_authenticated:
        
        try:
            
            model= request.user.id
            #filtering the listings using both the users id and the properties id(Hacked my way through this🤡)
            if request.user.username == admin:
                property1= PropertyManagementRent.objects.order_by('-listed_date')
                property2= PropertyManagementSale.objects.order_by('-listed_date')
                return render(request, 'all_listings.html', {'property1':property1, 'property2':property2})
            else:
                messages.warning(request, 'Youre not authorized to access this page be warned or you will be suspended!!!')
                logout_user(request)
                return redirect('customers_url:landing')
                
                
        except Exception as e:
            messages.error(f"an error occured {e}")
            return redirect('executive')
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('customers_url:landing')
    