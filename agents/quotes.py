# agent/quotes.py
import random

def get_random_quote():
    """Returns a random real estate quote with author"""
    
    quotes = [
        {
            'tips': 'Success in Real estate starts when you are worthy of it',
            'by': 'Michael Ferrara'
        },
        {
            'tips': "To be consistent in real estate, you must always and consistently put your clients' best interest first",
            'by': 'Anthony Hitt'
        },
        {
            'tips': 'Real Estate is the purest form of Entrepreneurship',
            'by': 'Brian Buffini'
        },
        {
            'tips': 'The best investment on Earth is earth',
            'by': 'Louis Glickman'
        },
        {
            'tips': 'Buy land, they\'re not making it anymore',
            'by': 'Mark Twain'
        },
        {
            'tips': 'Don\'t wait to buy real estate. Buy real estate and wait',
            'by': 'Will Rogers'
        },
        {
            'tips': 'Real estate cannot be lost or stolen, nor can it be carried away',
            'by': 'Franklin D. Roosevelt'
        },
        {
            'tips': 'Location, location, location',
            'by': 'Real Estate Wisdom'
        },
        {
            'tips': 'Ninety percent of all millionaires become so through owning real estate',
            'by': 'Andrew Carnegie'
        },
        {
            'tips': 'Every person who invests in well-selected real estate in a growing section of a prosperous community adopts the surest and safest method of becoming independent',
            'by': 'Theodore Roosevelt'
        },
        {
            'tips': 'Real estate investing, even on a very small scale, remains a tried and true means of building an individual\'s cash flow and wealth',
            'by': 'Robert Kiyosaki'
        },
        {
            'tips': 'The major fortunes in America have been made in land',
            'by': 'John D. Rockefeller'
        },
        {
            'tips': 'Now is always the right time to buy real estate',
            'by': 'Grant Cardone'
        },
        {
            'tips': 'Real estate is an imperishable asset, ever increasing in value',
            'by': 'Russell Sage'
        },
        {
            'tips': 'In real estate, you make 10% of your money because you\'re a genius and 90% because you catch a great wave',
            'by': 'Jeff Greene'
        },
        {
            'tips': 'Opportunity is missed by most people because it is dressed in overalls and looks like work',
            'by': 'Thomas Edison'
        },
        {
            'tips': 'The wise young man or wage earner of today invests his money in real estate',
            'by': 'Andrew Carnegie'
        },
        {
            'tips': 'Real estate is the closest thing to the proverbial pot of gold',
            'by': 'Ada Louise Huxtable'
        },
        {
            'tips': 'A funny thing happens in real estate. When it comes back, it comes back up like gangbusters',
            'by': 'Barbara Corcoran'
        },
        {
            'tips': 'If you don\'t own a home, buy one. If you own a home, buy another one. If you own two homes, buy a third. And lend your relatives the money to buy a home',
            'by': 'John Paulson'
        },
        {
            'tips': 'Real estate is about the safest investment in the world',
            'by': 'Michael Eisner'
        },
        {
            'tips': 'Landlords grow rich in their sleep without working, risking or economizing',
            'by': 'John Stuart Mill'
        },
        {
            'tips': 'The best time to buy a home is always five years ago',
            'by': 'Ray Brown'
        },
        {
            'tips': 'More money has been made in real estate than in all industrial investments combined',
            'by': 'Andrew Carnegie'
        },
        {
            'tips': 'Real estate investing is not a get-rich-quick scheme. It\'s a get-rich-slow scheme',
            'by': 'Robert Kiyosaki'
        },
{
            'tips': 'Success is not final, failure is not fatal: it is the courage to continue that counts',
            'by': 'Winston Churchill'
        },
        {
            'tips': 'The secret of getting ahead is getting started',
            'by': 'Mark Twain'
        },
        {
            'tips': 'I made my money by selling too soon',
            'by': 'Bernard Baruch'
        },
        {
            'tips': 'In the business world, the rearview mirror is always clearer than the windshield',
            'by': 'Warren Buffett'
        },
        {
            'tips': 'Your network is your net worth',
            'by': 'Porter Gale'
        },
        {
            'tips': 'Don\'t be afraid to give up the good to go for the great',
            'by': 'John D. Rockefeller'
        },
        {
            'tips': 'The best way to predict the future is to create it',
            'by': 'Peter Drucker'
        },
        {
            'tips': 'Real estate is my favorite asset class to build wealth',
            'by': 'Gary Keller'
        },
        {
            'tips': 'You cannot be anything you want to be - but you can be a lot more of who you already are',
            'by': 'Tom Rath'
        },
        {
            'tips': 'The only place success comes before work is in the dictionary',
            'by': 'Vidal Sassoon'
        },
        {
            'tips': 'Do not wait; the time will never be just right. Start where you stand',
            'by': 'Napoleon Hill'
        },
        {
            'tips': 'Price is what you pay, value is what you get',
            'by': 'Warren Buffett'
        },
        {
            'tips': 'It\'s not about having the right opportunities, it\'s about handling the opportunities right',
            'by': 'Mark Hunter'
        },
        {
            'tips': 'Real estate is the ultimate wealth builder',
            'by': 'Suze Orman'
        },
        {
            'tips': 'Brick and mortar businesses are great because they create an immense amount of wealth',
            'by': 'Robert Kiyosaki'
        },
        {
            'tips': 'Every great dream begins with a dreamer',
            'by': 'Harriet Tubman'
        },
        {
            'tips': 'The harder you work for something, the greater you\'ll feel when you achieve it',
            'by': 'Anonymous'
        },
        {
            'tips': 'Success usually comes to those who are too busy to be looking for it',
            'by': 'Henry David Thoreau'
        },
        {
            'tips': 'Don\'t watch the clock; do what it does. Keep going',
            'by': 'Sam Levenson'
        },
        {
            'tips': 'The difference between successful people and others is how long they spend feeling sorry for themselves',
            'by': 'Barbara Corcoran'
        },
        {
            'tips': 'Real estate is not about buildings, it\'s about people and their dreams',
            'by': 'Unknown'
        },
        {
            'tips': 'If you think you can do a thing or think you can\'t do a thing, you\'re right',
            'by': 'Henry Ford'
        },
        {
            'tips': 'The only limit to our realization of tomorrow is our doubts of today',
            'by': 'Franklin D. Roosevelt'
        },
        {
            'tips': 'Act as if what you do makes a difference. It does',
            'by': 'William James'
        },
        {
            'tips': 'Believe you can and you\'re halfway there',
            'by': 'Theodore Roosevelt'
        },
        {
            'tips': 'Everything you\'ve ever wanted is on the other side of fear',
            'by': 'George Addair'
        },
        {
            'tips': 'Success is liking yourself, liking what you do, and liking how you do it',
            'by': 'Maya Angelou'
        },
        {
            'tips': 'Start where you are. Use what you have. Do what you can',
            'by': 'Arthur Ashe'
        },
        {
            'tips': 'Quality is never an accident; it is always the result of intelligent effort',
            'by': 'John Ruskin'
        },
        {
            'tips': 'The key to success is to focus on goals, not obstacles',
            'by': 'Unknown'
        },
        {
            'tips': 'Real estate provides the highest returns, the greatest values, and the least risk',
            'by': 'Armstrong Williams'
        },
        {
            'tips': 'Your attitude, not your aptitude, will determine your altitude',
            'by': 'Zig Ziglar'
        },
        {
            'tips': 'If you\'re not embarrassed by the first version of your product, you\'ve launched too late',
            'by': 'Reid Hoffman'
        },
        {
            'tips': 'Dream big and dare to fail',
            'by': 'Norman Vaughan'
        },
        {
            'tips': 'The way to get started is to quit talking and begin doing',
            'by': 'Walt Disney'
        },
        {
            'tips': 'Don\'t let yesterday take up too much of today',
            'by': 'Will Rogers'
        },
        {
            'tips': 'You learn more from failure than from success',
            'by': 'Unknown'
        },
        {
            'tips': 'If you are working on something that you really care about, you don\'t have to be pushed',
            'by': 'Steve Jobs'
        },
        {
            'tips': 'People who succeed have momentum. The more they succeed, the more they want to succeed',
            'by': 'Tony Robbins'
        },
        {
            'tips': 'Don\'t be distracted by criticism. Remember, the only taste of success some people get is to take a bite out of you',
            'by': 'Zig Ziglar'
        },
        {
            'tips': 'The only impossible journey is the one you never begin',
            'by': 'Tony Robbins'
        },
        {
            'tips': 'Success is walking from failure to failure with no loss of enthusiasm',
            'by': 'Winston Churchill'
        },
        {
            'tips': 'I find that the harder I work, the more luck I seem to have',
            'by': 'Thomas Jefferson'
        },
        {
            'tips': 'The future belongs to those who believe in the beauty of their dreams',
            'by': 'Eleanor Roosevelt'
        },
        {
            'tips': 'It is never too late to be what you might have been',
            'by': 'George Eliot'
        },
        {
            'tips': 'A goal without a plan is just a wish',
            'by': 'Antoine de Saint-Exupéry'
        },
        {
            'tips': 'Opportunities don\'t happen. You create them',
            'by': 'Chris Grosser'
        },
        {
            'tips': 'Try not to become a person of success, but rather try to become a person of value',
            'by': 'Albert Einstein'
        },
        {
            'tips': 'Great things never come from comfort zones',
            'by': 'Anonymous'
        },
        {
            'tips': 'Success is not how high you have climbed, but how you make a positive difference to the world',
            'by': 'Roy T. Bennett'
        },
        {
            'tips': 'Don\'t be pushed around by the fears in your mind. Be led by the dreams in your heart',
            'by': 'Roy T. Bennett'
        },
        {
            'tips': 'The only way to do great work is to love what you do',
            'by': 'Steve Jobs'
        },
        {
            'tips': 'If you really look closely, most overnight successes took a long time',
            'by': 'Steve Jobs'
        },
        {
            'tips': 'The road to success and the road to failure are almost exactly the same',
            'by': 'Colin R. Davis'
        },
        {
            'tips': 'Success is getting what you want, happiness is wanting what you get',
            'by': 'W. P. Kinsella'
        },
        {
            'tips': 'Don\'t let what you cannot do interfere with what you can do',
            'by': 'John Wooden'
        },
        {
            'tips': 'You miss 100% of the shots you don\'t take',
            'by': 'Wayne Gretzky'
        },
        {
            'tips': 'Whether you think you can or you think you can\'t, you\'re right',
            'by': 'Henry Ford'
        },
        {
            'tips': 'The man who has confidence in himself gains the confidence of others',
            'by': 'Hasidic Proverb'
        },
        {
            'tips': 'The only person you are destined to become is the person you decide to be',
            'by': 'Ralph Waldo Emerson'
        },
        {
            'tips': 'Go confidently in the direction of your dreams. Live the life you have imagined',
            'by': 'Henry David Thoreau'
        },
        {
            'tips': 'When everything seems to be going against you, remember that the airplane takes off against the wind',
            'by': 'Henry Ford'
        },
        {
            'tips': 'It\'s not whether you get knocked down, it\'s whether you get up',
            'by': 'Vince Lombardi'
        },
        {
            'tips': 'Failure will never overtake me if my determination to succeed is strong enough',
            'by': 'Og Mandino'
        },
        {
            'tips': 'We may encounter many defeats but we must not be defeated',
            'by': 'Maya Angelou'
        },
        {
            'tips': 'Knowing is not enough; we must apply. Wishing is not enough; we must do',
            'by': 'Johann Wolfgang Von Goethe'
        },
        {
            'tips': 'The real test is not whether you avoid failure, because you won\'t. It\'s whether you let it harden or shame you',
            'by': 'Barack Obama'
        },
        {
            'tips': 'Success seems to be connected with action. Successful people keep moving',
            'by': 'Conrad Hilton'
        },
        {
            'tips': 'Life is 10% what happens to you and 90% how you react to it',
            'by': 'Charles R. Swindoll'
        },
        {
            'tips': 'The most difficult thing is the decision to act, the rest is merely tenacity',
            'by': 'Amelia Earhart'
        },
        {
            'tips': 'Every accomplishment starts with the decision to try',
            'by': 'John F. Kennedy'
        },
        {
            'tips': 'Don\'t limit yourself. Many people limit themselves to what they think they can do',
            'by': 'Mary Kay Ash'
        },
        {
            'tips': 'Real estate is a people business. It\'s about relationships',
            'by': 'Unknown'
        },
        {
            'tips': 'The best investment you can make is in yourself',
            'by': 'Warren Buffett'
        },
        {
            'tips': 'Action is the foundational key to all success',
            'by': 'Pablo Picasso'
        }
    ]
    
    return random.choice(quotes)

