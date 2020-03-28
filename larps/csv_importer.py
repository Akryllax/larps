import csv, io
from django.contrib.auth.models import User
from .models import *
from .config import larp_name, csv_file_types

# CREATE ELEMENTS (USERS, CHARACTERS...) BASED ON CSV INFORMATION

# Checks if the string provided is empty or only blank spaces
def empty(name):
    return not name.strip()

def get_larp(larp_name):
    larp_search = Larp.objects.filter(name=larp_name)
    if larp_search:
        return larp_search[0]
    else:
        larp = Larp(name=larp_name)
        larp.save()
        return larp

def create_user(player_name):
    if empty(player_name):
        return None

    name_parts = player_name.split(' ')
    username = "_".join(name_parts)
    first_name = name_parts[0]
    last_name = " ".join(name_parts[1:])

    user, created = User.objects.update_or_create(
        username=username,
        first_name=first_name,
        last_name=last_name
    )
    return user


def create_character(larp_name, character_name, character_group, character_race):
    if empty(character_name) and empty(character_group) and empty(character_race):
        return None

    larp = get_larp(larp_name)
    group, created = Group.objects.update_or_create(name=character_group, larp=larp)
    race, created = Race.objects.update_or_create(name=character_race)

    character, created = Character.objects.update_or_create(
        name=character_name,
        group=group,
        race=race
    )
    return character


def assign_character_to_user(user, character, run):
    _, created = CharacterAssigment.objects.update_or_create(
        run = run,
        character=character,
        user=user
    )
    if created:
        result = "Character "+ character.name + " assigned to " + user.first_name + " " + user.last_name
    else:
        result = "Not assigned."
    return result


# PROCESS CSV FILE

def process_character_info(column):
    # run	player	character	group	planet	rank
    run = column[0]
    player_name = column[1]
    character_name = column[2]
    character_group = column[3]
    character_race = column[4]

    user = create_user(player_name)
    character = create_character(larp_name(), character_name, character_group, character_race)

    if user and character:
        result = assign_character_to_user(user, character, run)
    else:
        if not user:
            result = "User invalid"
        else:
            result = "Created user " + user.first_name + " " + user.last_name
        if not character:
            result += ". Character invalid"
    return result

def create_uniform(uniform_name, group_name):
    larp = get_larp(larp_name())
    if not empty(group_name):
        group, created = Group.objects.update_or_create(name=group_name, larp=larp)
    else:
        group = None
    uniform, created = Uniform.objects.update_or_create(name=uniform_name, group=group)
    return uniform

def process_size_info(column):
    size_information = {}
    size_information["gender"] = column[3]
    size_information["american_size"] = column[4]
    size_information["european_size"] = column[5]
    size_information["chest_min"] = column[6]
    size_information["chest_max"] = column[7]
    size_information["waist_min"] = column[8]
    size_information["waist_max"] = column[9]
    return size_information

def process_uniform_info(column):
    # name ,group,color,gender,american_size,european_size,chest_min,chest_max,waist_min,waist_max
    uniform_name = column[0]
    group_name = column[1]
    uniform = create_uniform(uniform_name, group_name)
    if uniform:
        size_information = process_size_info(column)
        size = uniform.add_size(size_information)
        result = str(uniform) + " - " + str(size)
    else:
        result = "Uniform info NOT PROCESSED. " + str(column)
    return result

def process_csv_line(column, file_type):
    file_types_list = csv_file_types()
    if file_type == file_types_list[0][0]:
        result = process_character_info(column)
    elif file_type == file_types_list[1][0]:
        result = process_uniform_info(column)
    else:
        result = "File type "+ str(file_type) + " not recognised"
    return result

def process_data(data_set, file_type):
    result = []
    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        r = process_csv_line(column, file_type)
        result.append(r)
    return result

def read_csv_file(file):
    data_set = file.read().decode('UTF-8')
    return data_set

def process_csv(file, file_type):
    data_set = read_csv_file(file)
    result = process_data(data_set, file_type)
    return result
