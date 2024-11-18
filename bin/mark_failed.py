import pandas as pd
from psiturk.amt_services_wrapper import MTurkServicesWrapper, Participant, init_db, db_session
from sqlalchemy import or_, and_, exc
from psiturk.psiturk_statuses import *

wrapper = MTurkServicesWrapper()
amt = wrapper.amt_services
config = wrapper.config
init_db()

# %% ====================  ====================
VERSION = '2.3'
qdata = pd.read_csv(f'data/human_raw/{VERSION}/questiondata.csv', header=None)
qdata.columns = ['uid', 'key', 'val']
qdata[['workerid', 'assignmentid']] = qdata.uid.str.split(':', expand=True)

complete = set(qdata.query('key == "bonus"').uid)
# %% ====================  ====================
# incomplete = set(qdata.workerid) - complete

submitted = Participant.query.\
    filter(Participant.codeversion == VERSION).\
    filter(Participant.mode == 'live').\
    filter(or_(Participant.status == COMPLETED,
               Participant.status == CREDITED,
               Participant.status == SUBMITTED,
               Participant.status == BONUSED)).all()

n_change = 0
for p in submitted:
    if p.uniqueid not in complete:
        n_change += 1
        p.status = QUITEARLY
        db_session.add(p)

db_session.commit()

# %% ====================  ====================

import datetime
cutofftime = datetime.timedelta(minutes=-20)
starttime = datetime.datetime.now() + cutofftime

marked_wrong = Participant.query.filter(and_(
    Participant.status == QUITEARLY,
    Participant.beginhit > starttime
)).all()

for p in marked_wrong:
    if p.uniqueid in complete:
        p.status = 4
    else:
        p.status = 1
        db_session.add(p)
db_session.commit()