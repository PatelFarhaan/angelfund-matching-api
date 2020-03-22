import sys
sys.path.append('../')
from project.models import SignUpMappings


def sector_data():
    value = {'0': 'Agriculture / Agtech',
             '1': 'Artificial Intelligence',
             '2': 'Augmented Reality',
             '3': 'Biomedical',
             '4': 'Biotech',
             '5': 'Blockchain',
             '6': 'Community',
             '7': 'Crowdfunding',
             '8': 'Diversity',
             '9': 'Drones',
             '10': 'Education',
             '11': 'Enterprise',
             '12': 'Entertainment',
             '13': 'Esports / Online Gaming',
             '14': 'Financial / Banking',
             '15': 'Government',
             '16': 'Hardware',
             '17': 'Healthcare',
             '18': 'Marketplace',
             '19': 'Media / Advertising',
             '20': 'Moonshots / Hard Tech',
             '21': 'Robotics',
             '22': 'Security',
             '23': 'Sport/Fitness',
             '24': 'Transportation',
             '25': 'Travel',
             '26': 'Virtual Reality',
             '27': 'Other'}
    data = {
        "name": "sector_data",
        "value": value
    }
    return data


def deals_data():
    value = {
        "0": "$0 to $10,000",
        "1": "$10,000 to $25,000",
        "2": "$25,000 to $50,000",
        "3": "$50,000 to $100,000",
        "4": "$100,000 to $250,000",
        "5": "$250,000 to $500,000"
    }
    data = {
        "name": "deals_data",
        "value": value
    }
    return data


def accreditation_data():
    value = {
        "0": "I have a net worth of $1 million or more, excluding my primary home.",
        "1": "I have an individual annual income that has exceeded $200,000 for the last 2 years, and expect it to be the same or higher this year.",
        "2": "I have a joint annual income that has exceeded $300,000 for the last 2 years, and expect it to be the same or higher this year."
    }
    data = {
        "name": "accreditation_data",
        "value": value
    }
    return data


def main():
    SignUpMappings.objects.delete()
    insert_obj = SignUpMappings(
        deals_data=deals_data(),
        sector_data=sector_data(),
        accreditation_data=accreditation_data()
    )
    insert_obj.save()
    print("Inserted Successfully")