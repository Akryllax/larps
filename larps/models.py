from django.db import models
from django.contrib.auth.models import User


class Gender(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name


# PLAYER MEASUREMENT

class PlayerMeasurement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chest = models.IntegerField(default=0)
    arm_length = models.IntegerField(default=0)
    waist = models.IntegerField(default=0)
    shoulder_length = models.IntegerField(default=0)
    torso_length = models.IntegerField(default=0)
    body_length = models.IntegerField(default=0)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        if self.user.first_name:
            name = self.user.first_name + " " + self.user.last_name
        else:
            name = self.user.username
        return name

    def get_data(self):
        data = {
            'chest': self.chest,
            'arm_length': self.arm_length,
            'waist': self.waist,
            'shoulder_length': self.shoulder_length,
            'torso_length': self.torso_length,
            'body_length': self.body_length,
            'gender': self.gender,
        }
        return data

    def save_profile(self, new_data):
        self.chest = new_data['chest']
        self.arm_length = new_data['arm_length']
        self.waist = new_data['waist']
        self.shoulder_length = new_data['shoulder_length']
        self.torso_length = new_data['torso_length']
        self.body_length = new_data['body_length']
        self.gender = new_data['gender']
        self.save()


# LARPS AND CHARACTERS

class Larp(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name

    def get_character_assigments(self, run_id=None):
        groups = Group.objects.filter(larp=self)
        character_assigments = []
        for group in groups:
            assigments = group.get_character_assigments(run_id=run_id)
            character_assigments.extend(assigments)
        return character_assigments

    def get_number_of_runs(self, assigments=None):
        if not assigments:
            assigments = self.get_character_assigments()
        number_of_runs = 0
        for assigment in assigments:
            if assigment.run > number_of_runs:
                number_of_runs = assigment.run
        return number_of_runs

    @staticmethod
    def initialize_players_info(number_of_runs):
        players_info = []
        for _ in range(0, number_of_runs):
            players_info.append([])
        return players_info


    def get_players_information(self):
        assigments = self.get_character_assigments()
        number_of_runs = self.get_number_of_runs(assigments)
        players_info = self.initialize_players_info(number_of_runs)
        for assigment in assigments:
            profile = assigment.get_player_profile()
            bookings = assigment.get_bookings()
            if assigment.user:
                user_name = CharacterAssigment.compose_fullname(assigment)
            else:
                user_name = "Not assigned"
            info = {"user": user_name, "profile": profile, "bookings": bookings, "run": assigment.run, "character": assigment.character.name}
            run_index = assigment.run - 1
            players_info[run_index].append(info)
        return players_info

    def get_players_list_info(self, run_id=None) -> {}:
        """Returns all players info by Larp ID, (and optionally run)

        Parameters:
        run (int, optional): Run number

        Returns:
        dict: Dictionary, run ID index

        """

        assigments = None

        assigments = self.get_character_assigments(run_id=run_id)

        relevant_assignments = {}

        for assigment in assigments:
            if assigment.run not in relevant_assignments:
                relevant_assignments[assigment.run] = []

            info = {
                "run": assigment.run,
                "type": assigment.character.type.name,
                "fullname": CharacterAssigment.compose_fullname(assigment),
                "username": assigment.user.username,
                "email": assigment.user.email,
                "character": assigment.character.name,
                "group": assigment.character.group.name,
                "race": assigment.character.race.name,
                "rank": assigment.character.rank,
                "concept": assigment.character.concept if len(assigment.character.concept) > 1 else None,
                "character_sheet": assigment.character.sheet if len(assigment.character.sheet) > 1 else None,
                "read_friendly_character": assigment.character.easy_read_sheet if len(assigment.character.easy_read_sheet) > 1 else None,
                "user_discord": assigment.discord_email
            }

            relevant_assignments[assigment.run].append(info)

        return relevant_assignments


class Group(models.Model):
    larp = models.ForeignKey(Larp, on_delete=models.CASCADE)
    name = models.CharField(max_length=500, default="", blank=True)
    weapon = models.CharField(max_length=500, blank=True)

    def __str__(self):
        if self.name:
            return self.larp.name + " - " + self.name
        else:
            return self.larp.name + " - " + "no group"

    # returns the profiles of the players assigned to this group.
    def get_player_profiles(self):
        players = []
        character_assigments = self.get_character_assigments()
        for assigment in character_assigments:
            player_profile = assigment.get_player_profile()
            if player_profile:
                # check that the profile is not already on the list.
                if player_profile not in players:
                    players.append(player_profile)
        return players

    def get_character_assigments(self, run_id=None):
        character_assigments = []
        characters_list = Character.objects.filter(group=self)
        for character in characters_list:
            if run_id:
                assigments = CharacterAssigment.objects.filter(character=character, run=run_id)
            else:
                assigments = CharacterAssigment.objects.filter(character=character)
            character_assigments.extend(assigments)
        return character_assigments

    def character_assigment_for_user(self, user):
        character_assigments = self.get_character_assigments()
        user_assigments = []
        for assigment in character_assigments:
            if assigment.user == user:
                user_assigments.append(assigment)
        return user_assigments


class Race(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class CharacterType(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Character(models.Model):
    name = models.CharField(max_length=500)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    race = models.ForeignKey(Race, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.ForeignKey(CharacterType, on_delete=models.SET_NULL, null=True, blank=True)
    rank = models.CharField(max_length=500, blank=True)
    sheet = models.CharField(max_length=500, blank=True)
    easy_read_sheet = models.CharField(max_length=500, blank=True)
    concept = models.CharField(max_length=500, blank=True)
    weapon = models.CharField(max_length=500, blank=True)
    design_document = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.name


class CharacterAssigment(models.Model):
    run = models.IntegerField(default=1)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    discord_email = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        assigment = ""
        if self.character.group:
            assigment = self.character.group.larp.name + " run " + str(self.run) + " - " + self.character.name
        if self.user:
            assigment += " assigned to " + self.user.first_name + " " + self.user.last_name
        return assigment

    @staticmethod
    def compose_fullname(assigment) -> str:
        result = ""
        if assigment.user.first_name or assigment.user.last_name:
            result = assigment.user.first_name + " " + assigment.user.last_name
        else:
            result = assigment.user.username
        return result

    def larp(self):
        return self.character.group.larp

    def create_player_profile(self):
        player_profile = PlayerMeasurement(user=self.user)
        player_profile.save()
        return player_profile

    def get_player_profile(self):
        if not self.user:
            return None
        player_profiles = PlayerMeasurement.objects.filter(user=self.user)
        if player_profiles:
            return player_profiles[0]
        else:
            return self.create_player_profile()

    def get_bookings(self):
        larp = self.character.group.larp
        booking = None
        booking_search = Bookings.objects.filter(user=self.user, larp=larp, run=self.run)
        if booking_search:
            booking = booking_search[0]
        elif self.user:
            booking = Bookings(user=self.user, larp=larp, run=self.run)
            booking.save()
        return booking


# BOOKINGS

class Accomodation(models.Model):
    larp = models.ForeignKey(Larp, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class BusStop(models.Model):
    larp = models.ForeignKey(Larp, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Bookings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    larp = models.ForeignKey(Larp, on_delete=models.CASCADE)
    run = models.IntegerField(default=1)
    bus = models.ForeignKey(BusStop, on_delete=models.SET_NULL, null=True, blank=True)
    accomodation = models.ForeignKey(Accomodation, on_delete=models.SET_NULL, null=True, blank=True)
    sleeping_bag = models.BooleanField(null=True, blank=True)
    comments = models.CharField(max_length=500, default="no", blank=True, null=True)

    def __str__(self):
        text = ""
        if self.larp:
            text += self.larp.name + " run " + str(self.run)
        text += " - " + self.user.first_name + " " + self.user.last_name
        return text

    def get_data(self):
        data = {
            'bus': self.bus,
            'accomodation': self.accomodation,
            'sleeping_bag': self.sleeping_bag,
            'comments': self.comments
        }
        return data

    def save_bookings(self, new_data):
        self.bus = BusStop.objects.get(name=new_data['bus'])
        self.accomodation = Accomodation.objects.get(name=new_data['accomodation'])
        self.sleeping_bag = new_data['sleeping_bag']
        self.comments = new_data['comments']
        self.save()

    def get_character(self):
        assigments_search = CharacterAssigment.objects.filter(user=self.user, run=self.run)
        for assigment in assigments_search:
            if assigment.character.group.larp == self.larp:
                return assigment.character
        return None


# UNIFORMS

class Uniform(models.Model):
    name = models.CharField(max_length=500)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        text = self.name + " - "
        if self.group:
            text += self.group.name
        else:
            text += "group not assigned"
        return text

    def get_sizes(self):
        return UniformSize.objects.filter(uniform=self)

    def add_size(self, size_information):
        size = UniformSize(uniform=self)
        size.set_values(size_information)
        size.save()
        return size

    def find_perfect_fit(self, sizes, chest, waist):
        perfect_fit = []
        for size in sizes:
            if size.perfect_fit(chest, waist):
                perfect_fit.append(size)
        return perfect_fit

    def find_valid_fit(self, sizes, chest, waist):
        valid_fit = []
        for size in sizes:
            if (size.chest_fit(chest) and size.waist_minimum_fit(waist)):
                valid_fit.append(size)
            elif (size.chest_minimum_fit(chest) and size.waist_fit(waist)):
                valid_fit.append(size)
        if valid_fit:
            return valid_fit
        else:
            return None

    def recommend_sizes(self, player):
        sizes = self.get_sizes() #.filter(gender=player.gender)
        # TODO: Associate size to Character Assigment gender.
        if not sizes:
            return None
        perfect_fit = self.find_perfect_fit(sizes, player.chest, player.waist)
        if perfect_fit:
            return perfect_fit
        return self.find_valid_fit(sizes, player.chest, player.waist)

    def get_players_with_recommended_sizes(self):
        players_profiles = self.group.get_player_profiles()
        players_with_sizes = []
        for player in players_profiles:
            sizes = self.recommend_sizes(player=player)
            character_assigments = self.group.character_assigment_for_user(player.user)
            players_with_sizes.append( { "info": player, "sizes": sizes, "character_assigments": character_assigments } )
        return players_with_sizes

    def increment_quantity(self, sizes_with_quantities, size_to_increment):
        for size in sizes_with_quantities:
            if size["name"] == size_to_increment:
                size["quantity"] += 1

    def update_quantities(self, sizes_with_quantities, players_with_sizes):
        for player in players_with_sizes:
            if player["sizes"]:
                player_size = player["sizes"][0].get_name()
                self.increment_quantity(sizes_with_quantities, player_size)

    def initialize_sizes_with_quantities(self):
        sizes_with_quantities = []
        for size in self.get_sizes():
            sizes_with_quantities.append({ "name": size.get_name(), "info": size, "quantity": 0 })
        return sizes_with_quantities

    def get_sizes_with_quantities(self, players_with_sizes):
        sizes_with_quantities = self.initialize_sizes_with_quantities()
        self.update_quantities(sizes_with_quantities, players_with_sizes)
        return sizes_with_quantities


class UniformSize(models.Model):
    uniform = models.ForeignKey(Uniform, on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    american_size = models.CharField(max_length=500)
    european_size = models.CharField(max_length=500)
    chest_min = models.IntegerField()
    chest_max = models.IntegerField()
    waist_min = models.IntegerField()
    waist_max = models.IntegerField()

    def __str__(self):
        text = self.uniform.name + " "
        if self.gender:
            text = self.gender.name + ". "
        if self.american_size:
            text += str(self.american_size)
            if self.european_size:
                text += "/" + str(self.european_size) +" "
        elif self.european_size:
            str(self.european_size) +" "
        text += "chest(" + str(self.chest_min) + ","+ str(self.chest_max)+ ") "
        text += "waist(" + str(self.waist_min) + ","+ str(self.waist_max)+ ")"
        return text

    def get_name(self):
        name = self.american_size
        if name and self.european_size:
            name += " / " + self.european_size
        else:
            name = self.european_size
        return name

    def get_measurement(self, size_info, index):
        measurement = size_info[index]
        if not measurement:
            return 0
        return int(measurement)

    def set_values(self, size_info):
        gender_size = size_info["gender"]
        if gender_size=="": gender_size = "unisex"
        gender, _ = Gender.objects.get_or_create(name=gender_size)
        self.gender = gender
        self.american_size = size_info["american_size"]
        self.european_size = size_info["european_size"]
        self.chest_min = self.get_measurement(size_info, "chest_min")
        self.chest_max = self.get_measurement(size_info, "chest_max")
        self.waist_min = self.get_measurement(size_info, "waist_min")
        self.waist_max = self.get_measurement(size_info, "waist_max")

    def perfect_fit(self, chest, waist):
        return self.chest_fit(chest) and self.waist_fit(waist)

    def chest_fit(self, chest):
        return self.chest_min <= chest and self.chest_max >= chest

    def chest_minimum_fit(self, chest):
        return self.chest_fit(chest) or self.chest_min >= chest

    def waist_fit(self, waist):
        return self.waist_min <= waist and self.waist_max >= waist

    def waist_minimum_fit(self, waist):
        return self.waist_fit(waist) or self.waist_min >= waist
