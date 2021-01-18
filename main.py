# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import json
import os
import re
from pprint import pprint

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
        self.participants = []
    def add_participants(self, participants:list):
        self.participants.extend(participants)

    def add_utterance(self, utterance:Utterance):
        self.utterances.append(utterance)


def get_case_from_decision_data(case_data):
    with open(case_data['filename'], 'r', encoding='utf-8') as file:
        vote_data = json.loads(file.read())
        first_party = vote_data['first_party']
        second_party = vote_data['second_party']
        winning_party = vote_data['decisions'][0]['winning_party']
        justices = []
        for justice in vote_data['decisions'][0]['votes']:
            justices.append(
                Person(name=justice['member']['name'],
                       is_justice=True,
                       decision_type=justice['vote']))
        case = Case(case_name=vote_data['name'],
                    winner=winning_party,
                    party1=first_party,
                    party2=second_party)
        case.add_participants(justices)
        return case


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

decision_data_transcript_pairs = []
for case_datum in case_data:
    if case_datum['type'] == 'transcript':
        case_id_to_find = case_datum['case_id']
        decision_datum = [
            res for res in case_data if res['type'] == 'decision_data'
            and res['case_id'] == case_id_to_find
        ][0]
        decision_data_transcript_pairs.append((decision_datum, case_datum))

cases = []
for pair in decision_data_transcript_pairs:
    transcript_file = [file for file in pair
                       if file['type'] == 'transcript'][0]
    decision_data_file = [
        file for file in pair if file['type'] == 'decision_data'
    ][0]
    case_file = get_case_from_decision_data(decision_data_file)
    with open(transcript_file['filename'], 'r') as transcript:

        transcript = json.load(transcript)
        for section in transcript['transcript']['sections']:
            current_speaker = 'None'
            for turn in section['turns']:
                for participant in case_file.participants:
                    if participant.name == turn['speaker']['name']:
                        current_speaker = participant
                        #TODO: Add advocate names
                for text in turn['text_blocks']:
                    case_file.add_utterance(Utterance(current_speaker, text['text']))
        cases.append(case_file)
                    

# TODO: Add transcript parsing.
# transcript.sections[0].turns[1].text_blocks[0].text