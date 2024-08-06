import factory
from factory import Faker, SubFactory, post_generation
from random import randint
from .data_models import (Champion, TournamentCategoryInfo, Tournament, PlayerBio, Player,
                    PlayerRowV3, ScoringData, Hole, NineHoles, RoundScore, ScorecardV3,
                    PGATournament, PGAPlayer, PGALeaderboardPlayer, PGAPlayerScorecard, User)

class ChampionFactory(factory.Factory):
    class Meta:
        model = Champion

    displayName = Faker('name')
    playerId = Faker('uuid4')

class TournamentCategoryInfoFactory(factory.Factory):
    class Meta:
        model = TournamentCategoryInfo

    type = Faker('word')
    logoLight = Faker('image_url')
    logoDark = Faker('image_url')
    label = Faker('word')

class TournamentFactory(factory.Factory):
    class Meta:
        model = Tournament

    tournamentName = Faker('word')
    id = Faker('uuid4')
    beautyImage = Faker('image_url')
    champion = Faker('name')
    champions = factory.List([SubFactory(ChampionFactory) for _ in range(randint(1, 5))])
    championEarnings = Faker('currency')
    championId = Faker('uuid4')
    city = Faker('city')
    country = Faker('country')
    countryCode = Faker('country_code')
    courseName = Faker('word')
    date = Faker('date')
    dateAccessibilityText = Faker('sentence')
    purse = Faker('currency')
    sortDate = Faker('date')
    startDate = Faker('unix_time')
    state = Faker('state')
    stateCode = Faker('state_abbr')
    status = None
    tournamentStatus = None
    ticketsURL = None
    tourStandingHeading = Faker('word')
    tourStandingValue = Faker('word')
    tournamentLogo = Faker('image_url')
    display = Faker('word')
    sequenceNumber = Faker('random_int')
    tournamentCategoryInfo = SubFactory(TournamentCategoryInfoFactory)

class PlayerBioFactory(factory.Factory):
    class Meta:
        model = PlayerBio

    id = Faker('uuid4')
    age = Faker('random_int', min=18, max=50)
    education = Faker('word')
    turnedPro = Faker('random_int', min=2000, max=2020)

class PlayerFactory(factory.Factory):
    class Meta:
        model = Player

    id = Faker('uuid4')
    isActive = Faker('boolean')
    firstName = Faker('first_name')
    lastName = Faker('last_name')
    shortName = Faker('first_name')
    displayName = Faker('name')
    amateur = Faker('boolean')
    tourBound = Faker('boolean')
    alphaSort = None
    country = Faker('country')
    countryFlag = None
    headshot = None
    lineColor = None
    bettingProfile = None
    abbreviations = None
    abbreviationsAccessibilityText = None
    playerBio = SubFactory(PlayerBioFactory)

class ScoringDataFactory(factory.Factory):
    class Meta:
        model = ScoringData

    position = Faker('random_digit')
    total = None
    totalSort = None
    thru = None
    thruSort = None
    score = Faker('random_digit')
    scoreSort = Faker('random_digit')
    courseId = Faker('random_digit')
    groupNumber = Faker('random_digit')
    currentRound = Faker('random_digit')
    oddsToWin = None
    oddsSwing = None
    oddsOptionId = None
    oddsSort = None
    backNine = Faker('boolean')
    roundHeader = Faker('word')
    rounds = factory.List([Faker('random_digit') for _ in range(4)])
    movementDirection = Faker('word')
    movementAmount = Faker('random_digit')
    playerState = Faker('word')
    rankingMovement = None
    rankingMovementAmount = None
    rankingMovementAmountSort = None
    totalStrokes = Faker('random_digit')
    official = Faker('random_digit')
    officialSort = Faker('random_digit')
    projected = Faker('random_digit')
    projectedSort = Faker('random_digit')
    hasStoryContent = None
    storyContentRounds = factory.List([Faker('word') for _ in range(2)])
    roundStatus = None
    rankLogoLight = None
    rankLogoDark = None

class PlayerRowV3Factory(factory.Factory):
    class Meta:
        model = PlayerRowV3

    id = Faker('uuid4')
    leaderboardSortOrder = None
    player = SubFactory(PlayerFactory)
    scoringData = SubFactory(ScoringDataFactory)

class HoleFactory(factory.Factory):
    class Meta:
        model = Hole

    holeNumber = Faker('random_digit')
    par = Faker('random_digit')
    score = None
    sequenceNumber = None
    status = None
    yardage = None
    roundScore = None

class NineHolesFactory(factory.Factory):
    class Meta:
        model = NineHoles

    holes = factory.List([SubFactory(HoleFactory) for _ in range(9)])
    totalLabel = None
    parTotal = None
    total = None

class RoundScoreFactory(factory.Factory):
    class Meta:
        model = RoundScore

    complete = Faker('boolean')
    currentHole = Faker('random_digit')
    currentRound = Faker('boolean')
    firstNine = SubFactory(NineHolesFactory)
    secondNine = SubFactory(NineHolesFactory)
    roundNumber = Faker('random_digit')
    groupNumber = Faker('random_digit')
    courseName = Faker('word')
    courseId = Faker('random_digit')
    parTotal = Faker('random_digit')
    total = Faker('random_digit')
    scoreToPar = Faker('random_digit')

class ScorecardV3Factory(factory.Factory):
    class Meta:
        model = ScorecardV3

    tournamentName = Faker('word')
    id = Faker('uuid4')
    currentRound = Faker('random_digit')
    backNine = Faker('boolean')
    groupNumber = Faker('random_digit')
    player = SubFactory(PlayerFactory)
    roundScores = factory.List([SubFactory(RoundScoreFactory) for _ in range(4)])
    currentHole = Faker('random_digit')
    playerState = Faker('word')
    hideSov = Faker('boolean')
    profileEnabled = Faker('boolean')

class PGATournamentFactory(factory.Factory):
    class Meta:
        model = PGATournament

    id = Faker('uuid4')
    name = Faker('word')
    start_date = Faker('date')
    is_completed = Faker('boolean')
    data = SubFactory(TournamentFactory)
    last_updated = Faker('date_time_this_decade', tzinfo=None)

class PGAPlayerFactory(factory.Factory):
    class Meta:
        model = PGAPlayer

    id = Faker('uuid4')
    name = Faker('name')
    data = SubFactory(PlayerFactory)
    last_updated = Faker('date_time_this_decade', tzinfo=None)

class PGALeaderboardPlayerFactory(factory.Factory):
    class Meta:
        model = PGALeaderboardPlayer

    id = Faker('uuid4')
    tournament_id = Faker('uuid4')
    player_id = Faker('uuid4')
    data = SubFactory(PlayerRowV3Factory)
    last_updated = Faker('date_time_this_decade', tzinfo=None)

class PGAPlayerScorecardFactory(factory.Factory):
    class Meta:
        model = PGAPlayerScorecard

    id = Faker('uuid4')
    tournament_id = Faker('uuid4')
    player_id = Faker('uuid4')
    data = SubFactory(ScorecardV3Factory)
    last_updated = Faker('date_time_this_decade', tzinfo=None)

class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = Faker('uuid4')
    name = Faker('name')
    email = Faker('email')
    created = Faker('date_time_this_decade', tzinfo=None)
    last_updated = Faker('date_time_this_decade', tzinfo=None)
    last_login = Faker('date_time_this_decade', tzinfo=None)