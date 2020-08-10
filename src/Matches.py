class Match:
    '''
    A Class to hold the match id, if the primary team won
    and the picks and bans of the match
    '''
    def __init__(self, match, team_win):
        self.match = match
        self.team_win = team_win
        self.team_picks = []
        self.team_bans = []
        self.opponent_picks = []
        self.opponent_bans = []
