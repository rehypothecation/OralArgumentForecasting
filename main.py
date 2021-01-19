# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import json
import os
import re
from pprint import pprint
import csv


def get_df(justice:str, export_csv=False):
    class Person:
        def __init__(self,
                    name,
                    is_justice=False,
                    decision_type=None,
                    representing=None,
                    sided_with=None) -> None:
            super().__init__()
            self.name = name
            self.is_justice = is_justice
            self.representing = representing
            self.decision_type = decision_type
            self.sided_with = sided_with


    class Utterance:
        def __init__(self, speaker: Person, content: str, addressing=None):
            self.speaker = speaker
            self.content = content
            self.addressing = addressing


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

        def add_participants(self, participants: list):
            self.participants.extend(participants)

        def add_utterance(self, utterance: Utterance):
            self.utterances.append(utterance)

        def get_words_and_vote_by_justice(self, justice: str):
            res = [{
                'speaker': x.speaker.name,
                'content': x.content,
                'vote': x.speaker.decision_type
            } for x in cases[0].utterances
                if (x.speaker != None and justice in x.speaker.name)]

            return res


    def get_case_from_decision_data(case_data):
        with open(case_data['filename'], 'r', encoding='utf-8') as file:
            try:
                vote_data = json.loads(file.read())
                first_party = vote_data['first_party']
                second_party = vote_data['second_party']
                winning_party = 'petitioner' if vote_data['decisions'][0]['winning_party'][0:5] in first_party else 'respondent'
                justices = []
                for justice in vote_data['decisions'][0]['votes']:
                    sided_with = None
                    if justice['vote'] == 'majority' and winning_party == 'petitioner':
                        sided_with = 'petitioner'
                    elif justice['vote'] == 'concurrance' and winning_party == 'petitioner':
                        sided_with = 'petitioner'
                    elif justice['vote'] == 'minority' and winning_party == 'petitioner':
                        sided_with = 'respondent'
                    elif justice['vote'] == 'majority' and winning_party == 'respondent':
                        sided_with = 'respondent'
                    elif justice['vote'] == 'concurrance' and winning_party == 'respondent':
                        sided_with = 'respondent'
                    elif justice['vote'] == 'minority' and winning_party == 'respondent':
                        sided_with = 'petitioner'
                    elif justice['vote'] == 'minority' and winning_party == 'respondent':
                        sided_with = 'None'
                    justices.append(
                        Person(name=justice['member']['name'],
                            is_justice=True,
                            decision_type=justice['vote'],
                            sided_with=sided_with))
                case = Case(case_name=vote_data['name'],
                            winner=winning_party,
                            party1=first_party,
                            party2=second_party)
                case.add_participants(justices)
                n = 0
                for advocate in vote_data['advocates']:

                    case.add_participants([
                        Person(name=advocate['advocate']['name'],
                            is_justice=False,
                            decision_type=None,
                            representing="petitioner" if n == 0 else 'respondent')
                    ])
                    n += 1
                return case
            except TypeError:
                return None


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


    case_data = list(filetree('./data'))[: -6]

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
        if case_file is not None:
            with open(transcript_file['filename'], 'r', encoding='utf-8') as transcript:
                try:
                    transcript = json.load(transcript)
                    for section in transcript['transcript']['sections']:
                        previous_speaker = None
                        current_speaker = None
                        for turn in section['turns']:
                            for participant in case_file.participants:
                                try:
                                    if participant.name == turn['speaker']['name']:
                                        previous_speaker = current_speaker
                                        current_speaker = participant
                                except TypeError:
                                    pass
                            for text in turn['text_blocks']:
                                case_file.add_utterance(
                                    Utterance(current_speaker, text['text'], addressing=previous_speaker))

                    cases.append(case_file)
                except TypeError:
                    """
                    Some transcripts are damaged.
                    """
                    pass

    #%%


    res = []
    for case in cases:
        for utterance in case.utterances:
            if utterance.speaker != None and justice in utterance.speaker.name:
                res.append(utterance)

    lines_to_winning_party = []
    lines_to_losing_party = []
    try:
        for line in res:
            sided_with = line.speaker.sided_with
            name = line.speaker.name
            responding_to = line.addressing.representing
            content = line.content
            if sided_with != responding_to:
                lines_to_losing_party.append(line)
            elif sided_with == responding_to:
                lines_to_winning_party.append(line)
    except:
        pass

    import pandas as pd

    if export_csv:
        pd.DataFrame([line.content for line in lines_to_losing_party], columns=["text"]).to_csv(f"{justice}_loser.csv")
        pd.DataFrame([line.content for line in lines_to_winning_party], columns=["text"]).to_csv(f"{justice}_winner.csv")

    df = pd.DataFrame([[line.content for line in lines_to_winning_party], ['1']], columns= ['text', 'winning'])
    df.append()

    return pd.DataFrame([line.content for line in lines_to_winning_party], columns=["text",  "winning"])
# %%
# %%
get_df("Alito")
 