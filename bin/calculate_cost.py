#!/usr/bin/env python3
"""
Computes the cost of all HITs posted from the current psiturk project in a given month.

Usage:
pip install fire  # wonderful command line tool library
python calculate_cost.py
"""
import boto3
from psiturk.models import Participant
from datetime import datetime, timedelta
from sqlalchemy import and_, func

from fire import Fire 
from psiturk.psiturk_config import PsiturkConfig

def get_client():
    config = PsiturkConfig()
    config.load_config()
    return boto3.client('mturk',
        aws_access_key_id=config.get('AWS Access', 'aws_access_key_id'),
        aws_secret_access_key=config.get('AWS Access', 'aws_secret_access_key'),
        region_name='us-east-1'
    )

CLIENT = get_client()

def get_hits(from_date):
    # could be made more efficient by selecting unique values using sqlalchemy
    complete = (Participant.query
        .filter(and_(
            Participant.mode == 'live',
            func.date(Participant.beginhit) > from_date
        ))
        .all()
    )
    hit_ids = set(p.hitid for p in complete if not p.hitid.startswith('debug'))
    return (CLIENT.get_hit(HITId=h)['HIT'] for h in hit_ids if not h.startswith('prolific'))
    # hits =  list(CLIENT.get_hit(HITId=h)['HIT'] for h in hit_ids if not h.startswith('prolific'))
    # hits = list(hits)


last_year = str(datetime.now() - timedelta(days=3*365))
def calculate_cost(from_date=last_year, include_all=False):
    """Computes the cost of all HITs posted from the current psiturk project in a given month.

    By default the current year and month are used.
    Use include_all to show all HITs, not filtering by creation date.
    """
    total_cost = 0
    total_N = 0
    
    for hit in sorted(get_hits(from_date), key=lambda h: h['CreationTime']):
        dt = hit['CreationTime']
        # if not (include_all or (dt.year == year and dt.month == month)):
        #     continue
        N = hit['NumberOfAssignmentsCompleted']
        if N == 0:
            print(f"WARNING: No completed assignments for {hit['HITId']}. Maybe you haven't approved these assignments?")
        multiplier = 1.4 if hit['MaxAssignments'] > 9 else 1.2
        base = float(hit['Reward']) * N
        bonus = sum(float(x['BonusAmount']) for x in CLIENT.list_bonus_payments(HITId=hit['HITId'])['BonusPayments'])
        cost = 1.2 * bonus + multiplier * base
        print(f'{dt.date()}  {N} participants  ${cost:.2f}')
        total_N += N
        total_cost += cost
    print(f'TOTAL   {total_N:5d} participants  ${total_cost:.2f}')


if __name__ == '__main__':
    Fire(calculate_cost)
