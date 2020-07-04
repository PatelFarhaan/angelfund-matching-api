import sys
sys.path.append('../')


def rev_sector_data():
    return {'agtech': 'Agriculture / Agtech',
            'ai': 'Artificial Intelligence',
            'ar': 'Augmented Reality',
            'biomed': 'Biomedical',
            'biotech': 'Biotech',
            'blockchain': 'Blockchain',
            'community': 'Community',
            'crowdfund': 'Crowdfunding',
            'devtools': 'Developer Tools',
            'diversity': 'Diversity',
            'drones': 'Drones',
            'education': 'Education',
            'energy': 'Energy',
            'enterprise': 'Enterprise',
            'entertain': 'Entertainment',
            'gaming': 'Esports / Online Gaming',
            'banking': 'Financial / Banking',
            'government': 'Government',
            'hardware': 'Hardware',
            'health': 'Healthcare',
            'market': 'Marketplace',
            'media': 'Media / Advertising',
            'hardtech': 'Moonshots / Hard Tech',
            'robotics': 'Robotics',
            'security': 'Security',
            'sport': 'Sport / Fitness',
            'transport': 'Transportation',
            'travel': 'Travel',
            'vr': 'Virtual Reality',
            'other': 'Other'}


def rev_accreditation_data():
    return {'1000000': 'I have a net worth of $1 million or more, excluding my primary home.',
            '200000': 'I have an individual annual income that has exceeded $200,000 for the last 2 years, and expect it to be the same or higher this year.',
            '300000': 'I have a joint annual income that has exceeded $300,000 for the last 2 years, and expect it to be the same or higher this year.',
            'nothing': 'None of the above'}


def rev_progress_mapping():
    return  {'ideas': 'Idea/Sketches',
             'mockups': 'Mockups/Renderings',
             'prototype': 'Prototype/Pre-Launch',
             'beta': 'Beta Launched',
             'preorders': 'Taking Preorders',
             'product': 'Product Launched',
             'users': 'Early Users Acquired',
             'revenue': 'Early Revenue Generated'}