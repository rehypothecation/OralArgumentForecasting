# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import json
import os
import re
import requests


def filetree(top):
    for dirpath, _, fnames in os.walk(top):
        for fname in fnames:
            json_ = '(-t\d\d)*\.json'
            transcript_ = '-t\d\d\.json'
            yield {
                'filename':
                os.path.join(dirpath, fname),
                'case_id':
                re.sub(json_, '', fname),
                'type':
                'transcript'
                if re.search(transcript_, fname) else 'decision_data'
            }


case_data = list(filetree('./data'))


# %% [markdown]
# e.g. data <link>https://api.oyez.org/cases/2019/17-1623</link>


# %%
class Person:
    def __init__(self,
                 name,
                 is_justice=False,
                 decision_type=None,
                 representing=None) -> None:
        super().__init__()
        self.name = name
        self.is_justice = is_justice
        self.representing = representing
        self.decision_type = decision_type


class Utterance:
    def __init__(self, speaker: Person, content: str):
        self.speaker = speaker
        self.content = content


class Case:
    def __init__(self,
                 case_name,
                 winner,
                 party1,
                 party2,
                 utterances: list = []):
        self.casename = case_name
        self.utterances = utterances
        self.winner = winner
        self.party1 = party1
        self.party = party2


cases = []
people = []
"""
Assign justice votes to names from file.
"""

for case_data in cases:
    with open(case_data['filename'], 'r', encoding='utf-8') as file:
        vote_data = json.loads(file.read())
        first_party = vote_data['first_party']
        second_party = vote_data['second_party']
        winning_party = vote_data['decisions'][0]['winning_party']
        losing_party = first_party if (
            first_party != winning_party) else second_party
        for justice in vote_data['decisions'][0]['votes']:
            people.append(
                Person(name=justice['member']['name'],
                    is_justice=True,
                    decision_type=justice['vote']))
        cases.append(Case(case_name=vote_data['name'],winner=winning_party, party1=first_party,
                    party2=second_party))

# TODO: Add transcript parsing and zips.
results = []
for d in case_data:
    if d['type'] == 'transcript':
        case_id_to_find = d['case_id']
        dd = [res for res in case_data if res['type'] == 'decision_data' and res['case_id'] == case_id_to_find][0]
        results.append(zip(
           dd, d
        )
    )
list(results[0])

# %%
