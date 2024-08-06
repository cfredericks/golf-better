"""
Marshmallow schemas for converting from database to application data models, and also
the format for Postgres jsonb columns.
"""

from marshmallow import Schema, fields, post_load
from .data_models import Champion, TournamentCategoryInfo, Tournament, Player, PlayerBio, \
    PlayerRowV3, ScoringData, Hole, NineHoles, RoundScore, ScorecardV3, PGATournament, \
    PGAPlayer, PGAPlayerScorecard, PGALeaderboardPlayer, User

class ChampionSchema(Schema):
    displayName = fields.Str()
    playerId = fields.Str()

    @post_load
    def make_champion(self, data, **kwargs):
        return Champion(**data)

class TournamentCategoryInfoSchema(Schema):
    type = fields.Str()
    logoLight = fields.Str(allow_none=True, load_default=None)
    logoDark = fields.Str(allow_none=True, load_default=None)
    label = fields.Str(allow_none=True, load_default=None)

    @post_load
    def make_tournament_category_info(self, data, **kwargs):
        return TournamentCategoryInfo(**data)

class TournamentSchema(Schema):
    tournamentName = fields.Str()
    id = fields.Str()
    beautyImage = fields.Str()
    champion = fields.Str()
    champions = fields.List(fields.Nested(ChampionSchema))
    championEarnings = fields.Str()
    championId = fields.Str()
    city = fields.Str()
    country = fields.Str()
    countryCode = fields.Str()
    courseName = fields.Str()
    date = fields.Str()
    dateAccessibilityText = fields.Str()
    purse = fields.Str()
    sortDate = fields.Str()
    startDate = fields.Int()
    state = fields.Str()
    stateCode = fields.Str()
    status = fields.Str(allow_none=True, load_default=None)
    tournamentStatus = fields.Str(allow_none=True, load_default=None)
    ticketsURL = fields.Str(allow_none=True, load_default=None)
    tourStandingHeading = fields.Str()
    tourStandingValue = fields.Str()
    tournamentLogo = fields.Str()
    display = fields.Str()
    sequenceNumber = fields.Int()
    tournamentCategoryInfo = fields.Nested(TournamentCategoryInfoSchema, allow_none=True, load_default=None)

    @post_load
    def make_tournament(self, data, **kwargs):
        return Tournament(**data)

class PlayerBioSchema(Schema):
    id = fields.Str()
    age = fields.Int()
    education = fields.Str()
    turnedPro = fields.Int()

    @post_load
    def make_player_bio(self, data, **kwargs):
        return PlayerBio(**data)

class PlayerSchema(Schema):
    id = fields.Str()
    isActive = fields.Bool(allow_none=True, load_default=None)
    firstName = fields.Str()
    lastName = fields.Str()
    shortName = fields.Str()
    displayName = fields.Str()
    amateur = fields.Bool(allow_none=True, load_default=None)
    tourBound = fields.Bool(allow_none=True, load_default=None)
    alphaSort = fields.Str(allow_none=True, load_default=None)
    country = fields.Str()
    countryFlag = fields.Str(allow_none=True, load_default=None)
    headshot = fields.Str(allow_none=True, load_default=None)
    lineColor = fields.Str(allow_none=True, load_default=None)
    bettingProfile = fields.Str(allow_none=True, load_default=None)
    abbreviations = fields.Str(allow_none=True, load_default=None)
    abbreviationsAccessibilityText = fields.Str(allow_none=True, load_default=None)
    playerBio = fields.Nested(PlayerBioSchema, allow_none=True, load_default=None)

    @post_load
    def make_player(self, data, **kwargs):
        return Player(**data)

class ScoringDataSchema(Schema):
    position = fields.Str()
    total = fields.Str(allow_none=True, load_default=None)
    totalSort = fields.Int(allow_none=True, load_default=None)
    thru = fields.Str(allow_none=True, load_default=None)
    thruSort = fields.Int(allow_none=True, load_default=None)
    score = fields.Str()
    scoreSort = fields.Int()
    courseId = fields.Str()
    groupNumber = fields.Int()
    currentRound = fields.Int()
    oddsToWin = fields.Str(allow_none=True, load_default=None)
    oddsSwing = fields.Str(allow_none=True, load_default=None)
    oddsOptionId = fields.Str(allow_none=True, load_default=None)
    oddsSort = fields.Float(allow_none=True, load_default=None)
    backNine = fields.Bool()
    roundHeader = fields.Str()
    rounds = fields.List(fields.Str())
    movementDirection = fields.Str()
    movementAmount = fields.Str()
    playerState = fields.Str()
    rankingMovement = fields.Str(allow_none=True, load_default=None)
    rankingMovementAmount = fields.Str(allow_none=True, load_default=None)
    rankingMovementAmountSort = fields.Int(allow_none=True, load_default=None)
    totalStrokes = fields.Str()
    official = fields.Str()
    officialSort = fields.Int()
    projected = fields.Str()
    projectedSort = fields.Int()
    hasStoryContent = fields.Bool(allow_none=True, load_default=None)
    storyContentRounds = fields.List(fields.Str())
    roundStatus = fields.Str(allow_none=True, load_default=None)
    rankLogoLight = fields.Str(allow_none=True, load_default=None)
    rankLogoDark = fields.Str(allow_none=True, load_default=None)

    @post_load
    def make_scoring_data(self, data, **kwargs):
        return ScoringData(**data)

class PlayerRowV3Schema(Schema):
    id = fields.Str()
    leaderboardSortOrder = fields.Int(allow_none=True, load_default=None)
    player = fields.Nested(PlayerSchema)
    scoringData = fields.Nested(ScoringDataSchema)

    @post_load
    def make_player_row_v3(self, data, **kwargs):
        return PlayerRowV3(**data)

class HoleSchema(Schema):
    holeNumber = fields.Int()
    par = fields.Int()
    score = fields.Str(allow_none=True, load_default=None)
    sequenceNumber = fields.Int(allow_none=True, load_default=None)
    status = fields.Str(allow_none=True, load_default=None)
    yardage = fields.Int(allow_none=True, load_default=None)
    roundScore = fields.Str(allow_none=True, load_default=None)

    @post_load
    def make_hole(self, data, **kwargs):
        return Hole(**data)

class NineHolesSchema(Schema):
    holes = fields.List(fields.Nested(HoleSchema))
    totalLabel = fields.Str(allow_none=True, load_default=None)
    parTotal = fields.Int(allow_none=True, load_default=None)
    total = fields.Str(allow_none=True, load_default=None)

    @post_load
    def make_nine_holes(self, data, **kwargs):
        return NineHoles(**data)

class RoundScoreSchema(Schema):
    complete = fields.Bool()
    currentHole = fields.Int()
    currentRound = fields.Bool()
    firstNine = fields.Nested(NineHolesSchema)
    secondNine = fields.Nested(NineHolesSchema)
    roundNumber = fields.Int()
    groupNumber = fields.Int()
    courseName = fields.Str()
    courseId = fields.Str()
    parTotal = fields.Int()
    total = fields.Str()
    scoreToPar = fields.Str()

    @post_load
    def make_round_score(self, data, **kwargs):
        return RoundScore(**data)

class ScorecardV3Schema(Schema):
    tournamentName = fields.Str()
    id = fields.Str()
    currentRound = fields.Int()
    backNine = fields.Bool()
    groupNumber = fields.Int()
    player = fields.Nested(PlayerSchema)
    roundScores = fields.List(fields.Nested(RoundScoreSchema))
    currentHole = fields.Int()
    playerState = fields.Str()
    hideSov = fields.Bool()
    profileEnabled = fields.Bool()

    @post_load
    def make_scorecard_v3(self, data, **kwargs):
        return ScorecardV3(**data)

class PGATournamentSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    start_date = fields.Date()
    is_completed = fields.Bool()
    data = fields.Nested(TournamentSchema)
    last_updated = fields.DateTime()

    @post_load
    def make_pga_tournament(self, data, **kwargs):
        return PGATournament(**data)

class PGAPlayerSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    data = fields.Nested(PlayerSchema)
    last_updated = fields.DateTime()

    @post_load
    def make_pga_player(self, data, **kwargs):
        return PGAPlayer(**data)

class PGALeaderboardPlayerSchema(Schema):
    id = fields.Str()
    tournament_id = fields.Str()
    player_id = fields.Str()
    data = fields.Nested(PlayerRowV3Schema)
    last_updated = fields.DateTime()

    @post_load
    def make_pga_leaderboard_player(self, data, **kwargs):
        return PGALeaderboardPlayer(**data)

class PGAPlayerScorecardSchema(Schema):
    id = fields.Str()
    tournament_id = fields.Str()
    player_id = fields.Str()
    data = fields.Nested(ScorecardV3Schema)
    last_updated = fields.DateTime()

    @post_load
    def make_pga_player_scorecard(self, data, **kwargs):
        return PGAPlayerScorecard(**data)

class UserSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    email = fields.Str()
    created = fields.DateTime()
    last_updated = fields.DateTime()
    last_login = fields.DateTime()

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)
