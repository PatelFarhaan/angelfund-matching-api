#<==================================================================================================>
#                                         IMPORTS
#<==================================================================================================>
import sys
sys.path.append('../')


#<==================================================================================================>
#                                      SECTORS DATA
#<==================================================================================================>
def sector_data():
    return {'Agriculture / Agtech': 'agtech',
            'Artificial Intelligence': 'ai',
            'Augmented Reality': 'ar',
            'Biomedical': 'biomed',
            'Biotech': 'biotech',
            'Blockchain': 'blockchain',
            'Community': 'community',
            'Crowdfunding': 'crowdfund',
            'Developer Tools': 'devtools',
            'Diversity': 'diversity',
            'Drones': 'drones',
            'Education': 'education',
            'Energy': 'energy',
            'Enterprise': 'enterprise',
            'Entertainment': 'entertain',
            'Esports / Online Gaming': 'gaming',
            'Financial / Banking': 'banking',
            'Government': 'government',
            'Hardware': 'hardware',
            'Healthcare': 'health',
            'Marketplace': 'market',
            'Media / Advertising': 'media',
            'Moonshots / Hard Tech': 'hardtech',
            'Robotics': 'robotics',
            'Security': 'security',
            'Sport/Fitness': 'sport',
            'Transportation': 'transport',
            'Travel': 'travel',
            'Virtual Reality': 'vr',
            'Other': 'other'}


#<==================================================================================================>
#                                  ACCREDITATION DATA
#<==================================================================================================>
def accreditation_data():
    return {
        "I have a net worth of $1 million or more, excluding my primary home.": "1000000",
        "I have an individual annual income that has exceeded $200,000 for the last 2 years, and expect it to be the same or higher this year.": "200000",
        "I have a joint annual income that has exceeded $300,000 for the last 2 years, and expect it to be the same or higher this year.": "300000",
        "None of the above": "nothing"
    }

#<==================================================================================================>
#                                  PROGRESS MAPPING
#<==================================================================================================>
def progress_mapping():
    return  {
        'Idea/Sketches': 'ideas',
        'Mockups/Renderings': 'mockups',
        'Prototype/Pre-Launch': 'prototype',
        'Beta Launched': 'beta',
        'Taking Preorders': 'preorders',
        'Product Launched': 'product',
        'Early Users Acquired': 'users',
        'Early Revenue Generated': 'revenue'
    }


#<==================================================================================================>
#                               ROUND SIZE TO DEALS COMMON MAPPING
#<==================================================================================================>
def round_def(number):
    if 0 <= number <= 10000:
        return "0"
    elif 10000 <= number <= 25000:
        return "10"
    elif 25000 <= number <= 50000:
        return "25"
    elif 50000 <= number <= 100000:
        return "50"
    elif 100000 <= number <= 250000:
        return "100"
    elif 250000 <= number <= 500000:
        return "250"
    elif number > 500000:
        return "500"