#!/usr/bin/python
# -*- coding: utf-8 -*
import fileinput
import json
import math
import random
from flask import Flask, request, jsonify
from flask import render_template
from flaskwebgui import FlaskUI

app = Flask(__name__)
ui = FlaskUI(app)


@app.route('/')
def index():
    """
    Index
    :return: page
    """

    # Menu option
    menu_option = get_menu_option()

    # Places
    places = get_places()

    # Team
    team = get_team()

    # Spots
    spots = get_spots(places)

    return render_template(template_name_or_list="index.html",
                           menu_option=menu_option,
                           team=team,
                           places=places,
                           spots=spots,
                           shift=get_shift_json_content())


@app.route('/add_member')
def add_member():
    """
    Add member
    :return: void
    """
    member_name = request.args.get('member_name', '')
    print("New team member{}|".format(member_name))
    write_member_in_team_file(member_name)
    return jsonify("")


@app.route('/remove_member')
def remove_member():
    """
    Remove member
    :return: void
    """
    # Member name passed as arg
    member_name = request.args.get('member_name', '')

    json_data = get_team_json_content()

    for i, member in enumerate(json_data['member']):
        print(json_data['member'][i]['name'])
        if json_data['member'][i]['name'] == member_name:
            print("removing some data = {}".format(json_data))
            del json_data['member'][i]

    set_team_json_content(json_data)
    print("Member{}".format(member_name))
    return jsonify("")


@app.route('/set_skill')
def set_skill():
    """
    Set skill
    :return: skill
    """
    # Get params
    skill_index = request.args.get('skill_id', '')
    skill_id = skill_index.split('/')[0]
    member_name = skill_index.split('/')[1]
    print("skill id {}".format(skill_id))
    print("member name{}".format(member_name))
    print(math.floor(int(skill_id)))
    skill_id = math.floor(int(skill_id))
    json_data = get_team_json_content()
    json_data = switch_on_off_skills(json_data, member_name, skill_id)
    set_team_json_content(json_data)
    return jsonify(skill_id)


def switch_on_off_skills(team_json_data, member_name, skill_id, switch_off_is_requested=True):
    """
    Switch on off skills
    :param switch_off_is_requested: boolean to activate the removing of skill
    :param team_json_data: team json data
    :param member_name: member name
    :param skill_id: skill id
    :return: team json data with switched skills
    """
    # UPDATE - Update member skills
    for i, member in enumerate(team_json_data['member']):
        if team_json_data['member'][i]['name'] == member_name:
            print("Skill id update{}".format(team_json_data['member'][i]['skills'][skill_id]))
            if 'X' in team_json_data['member'][i]['skills'][skill_id] and switch_off_is_requested:
                team_json_data['member'][i]['skills'][skill_id] = ''
            else:
                team_json_data['member'][i]['skills'][skill_id] = 'X'

    return team_json_data


@app.route('/save_menu_option')
def save_menu_option():
    """
    Save menu option
    :return: json
    """
    menu_option = request.args.get('menu_option', '')
    print(menu_option)
    with open("menu", "w") as menu:
        menu.write(menu_option)
    return jsonify(menu_option)


@app.route('/set_position')
def set_position():
    """
    Set position
    :return: position
    """
    # Get params
    place_id = request.args.get('place_id', '')
    place_name = request.args.get('place_name', '').replace("P", "")
    print("name {}".format(place_name))
    print("index{}".format(place_id))
    print(math.floor(int(place_id)))
    write_in_table_file(place_id, place_name)
    return jsonify(place_id)


@app.route('/validate_shift')
def validate_shift():
    """
    Validate shift
    :return: json status
    """
    shift = get_shift_json_content()
    team = get_team_json_content()
    for skill_id, member in enumerate(shift):
        team = switch_on_off_skills(team, member, skill_id, switch_off_is_requested=False)
        print(team)
    print(team)
    set_team_json_content(team)
    return jsonify(team)


def get_shift_with_skilled_members():
    """
    Show what place a member should occupy
    :return:
    """
    shift_with_skilled_members = []
    for i, shift_list in enumerate(get_qualified_members()):
        for i_member, spot_member in enumerate(shift_list):
            spot_member = list(filter(None, spot_member))
            if len(spot_member) <= 1:
                if isinstance(spot_member, list) and len(spot_member) == 1:
                    spot_member = spot_member[0]
                else:
                    spot_member = ''

                shift_with_skilled_members.append(spot_member)
            else:
                shift_with_skilled_members.append('')

    return shift_with_skilled_members


def assign_member_where_only_them_fit(parsed_shift, qualified_members):
    """
    Show what place a member should occupy
    :return: shift
    """

    for i, shift_spot in enumerate(parsed_shift):
        shift_spot = list(filter(None, shift_spot))
        if len(shift_spot) <= 1:
            if isinstance(shift_spot, list) and len(shift_spot) >= 1 and len(shift_spot[0]) > 1:
                if shift_spot[0] not in qualified_members:
                    shift_spot = shift_spot[0]
            else:
                shift_spot = ''

            if shift_spot != '':
                print(i)
                print(parsed_shift[i])
                if isinstance(shift_spot, list) and len(shift_spot) >= 1:
                    parsed_shift[i] = shift_spot[0]
                else:
                    parsed_shift[i] = shift_spot
        else:
            if isinstance(shift_spot, list) and len(shift_spot) > 1 and len(shift_spot[0]) > 1:
                if shift_spot[0] not in qualified_members:
                    parsed_shift[i] = shift_spot[0]

    for i, shift_spot in enumerate(parsed_shift):
        if isinstance(shift_spot, list) and len(shift_spot) > 1:
            parsed_shift[i] = list(filter(None, shift_spot))
        elif isinstance(shift_spot, list) and len(shift_spot) >= 1:
            if shift_spot[0] not in qualified_members:
                parsed_shift[i] = shift_spot[0]
    print(parsed_shift)
    return parsed_shift


def remove_already_assigned_members(list_of_already_assigned_members, shift):
    """
    Remove already assigned members
    :param list_of_already_assigned_members:
    :param shift:
    :return: shift
    """
    for assigned_member in list_of_already_assigned_members:
        for shift_spot in shift:
            if isinstance(shift_spot, list) and len(shift_spot) > 1 and assigned_member in shift_spot:
                shift_spot.remove(assigned_member)
    print(shift)
    return shift


def there_is_a_list_with_different_members_in_shift(shift):
    """
    there_is_a_list_with_different_members_in_shift
    :param shift:
    :return:
    """
    there_is_a_list_with_different_members = False
    for shift_spot in shift:
        if isinstance(shift_spot, list) and len(shift_spot) > 1:
            there_is_a_list_with_different_members = True
            break

    return there_is_a_list_with_different_members


def shift_with_members_only_assigned_one_time(shift, list_of_overbooked_members, shift_with_skilled_members):
    for overbooked_member in list_of_overbooked_members:
        print(overbooked_member)
        skills = []
        for experience_index, experience in enumerate(shift_with_skilled_members):
            if overbooked_member in experience:
                skills.append(experience_index)
        print(skills)
        for shift_index, shift_spot in enumerate(shift):
            if overbooked_member in shift_spot:
                if shift_index not in skills:
                    shift[shift_index] = ''

    return shift


def tell_me_who_can_be_placed_please(shift, team_members):
    for spoted_member in shift:
        if spoted_member in team_members:
            team_members.remove(spoted_member)
    return team_members


@app.route('/create_shift')
def create_shift():
    """
    Create shift
    :return: json status
    """
    [shift, qualified_members] = get_qualified_members()
    while there_is_a_list_with_different_members_in_shift(shift):
        shift = assign_member_where_only_them_fit(shift, qualified_members)
        shift = remove_already_assigned_members(get_already_assigned_members(shift), shift)

    shift = convert_list_in_shift_to_string(shift)
    list_of_overbooked_members = get_list_of_members_assigned_in_different_spots(shift)
    shift_with_skilled_members = get_shift_with_skilled_members()
    shift = shift_with_members_only_assigned_one_time(shift, list_of_overbooked_members, shift_with_skilled_members)
    available_members = tell_me_who_can_be_placed_please(shift, team_members=get_team_members())
    for shift_index, shift_spot in enumerate(shift):
        if not shift_spot:
            for available_member in available_members:
                shift[shift_index] = available_member
                available_members.remove(available_member)
                break

    with open('shift.json', 'w', encoding='utf8') as outfile:
        json.dump(shift, outfile)

    return jsonify(shift)


def convert_list_in_shift_to_string(shift):
    new_shift = []
    for shift_spot in shift:
        while isinstance(shift_spot, list) and len(shift_spot) >= 1:
            shift_spot = shift_spot[0]
        new_shift.append(shift_spot)
    shift = new_shift
    return shift


def get_list_of_members_assigned_in_different_spots(shift):
    members_assigned_in_different_spot = []
    for team_member in get_team_members():
        team_member_count = 0
        for member in shift:
            if member == team_member:
                team_member_count += 1
        if team_member_count > 1:
            members_assigned_in_different_spot.append(team_member)
    return members_assigned_in_different_spot


def get_already_assigned_members(shift):
    already_assigned_members = []
    for shift_spot in shift:
        if isinstance(shift_spot, str):
            already_assigned_members.append(shift_spot)
    return already_assigned_members


def get_empty_shift_based_on_spots():
    """
    Create empty shift based on spot
    :return: shift
    """
    shift = []
    for i, shift_spot in enumerate(get_spots(get_places())):
        shift.append("")
    return shift


def fill_shift_randomly(shift):
    """
    Fill shift randowly
    :param shift: shift (maybe partly empty)
    :return: team and shif
    """

    for i, member in enumerate(shift):
        if shift.count(member) > 1:
            shift[i] = ''

    team = remove_assigned_member_to_team(shift, get_team_members())
    for i, shift_spot in enumerate(shift):
        if not shift_spot and team:
            member = random.choice(team)
            shift[i] = member
            team.remove(member)

    return shift


def remove_assigned_member_to_team(shift, team):
    """
    Remove assigned member to team
    :param shift: shift
    :param team: team
    :return: team with no duplicated member
    """

    for member in shift:
        if team is not None and member in team:
            team.remove(member)

    return team


def get_table():
    """
    Get table
    :return: places lines
    """
    with open("table.txt", encoding='utf8') as f:
        places_lines = f.readlines()
    return places_lines


def get_menu_option():
    """
    Get menu option
    :return:
    """
    with open("menu", encoding='utf8') as f:
        menu_option = f.readlines()
        if menu_option and isinstance(menu_option, list):
            menu_option = menu_option[0]
        else:
            menu_option = "0"
    return menu_option


def get_places():
    """
    Get places
    :return: places
    """
    places = []
    places_lines = get_table()
    for i, line in enumerate(places_lines):
        places.append(line.replace("{}=".format(i), "").replace("\n", "").replace(" ", ""))
    return places


def get_team():
    """
    Get team
    :return: team
    """
    team = []

    json_data = get_team_json_content()

    for i, member in enumerate(json_data['member']):
        member_name = json_data['member'][i]['name']
        member_skills = json_data['member'][i]['skills']
        member = [member_name, member_skills]
        team.append(member)

    return team


def write_member_in_team_file(member_name):
    """
    Add member in file
    :param member_name:
    :return:
    """

    skills = make_a_list_of_skills()
    json_data = get_team_json_content()

    # ADD TO JSON - Add member ton json data
    json_data['member'].append({
        'name': member_name,
        'skills': skills
    })

    set_team_json_content(json_data)


def set_team_json_content(json_data):
    """
    Set team json content
    :param json_data: json data
    :return: void
    """
    # SET JSON - Write modified json data
    with open('team.json', 'w', encoding='utf8') as outfile:
        json.dump(json_data, outfile)


def get_team_json_content():
    """
    Get team json content
    :return: json data
    """
    # GET JSON- Get json data
    with open('team.json') as json_file:
        json_data = json.load(json_file)
    return json_data


def get_shift_json_content():
    """
    Get shift json content
    :return: json data
    """
    # GET JSON- Get json data
    with open('shift.json') as json_file:
        json_data = json.load(json_file)
    return json_data


def make_a_list_of_skills():
    """
    Make a list of skills
    :return: list of skills
    """
    skills = []

    for _ in get_spots(places=get_places()):
        skills.append('')

    return skills


def write_in_table_file(place_id, place_name):
    """
    Write in table file
    :param place_id:
    :param place_name:
    :return:
    """
    # Write in table file
    for line in fileinput.FileInput("table.txt", inplace=1):
        if line.startswith("{}=".format(math.floor(int(place_id)))):
            # Add position
            print("{}={}".format(place_id, place_name))
        else:
            # Rewrite unchanged position
            print(line)

    # Remove break line
    for line in fileinput.FileInput("table.txt", inplace=1):
        if "=" in line:
            print(line.replace("\n", " "))


def select_random_member_in_team(team):
    """
    Select random member in team
    :param team: team
    :return: random team member
    """
    # Choose in team
    selected_member = random.choice(team)
    return selected_member


def get_team_members():
    """
    Get team members
    :return: team members
    """
    json_data = get_team_json_content()
    team_data = json_data['member']
    team = []
    for member in team_data:
        team.append(member['name'])
    return team


def set_a_member_in_only_one_place(shift):
    """
    Set a team member in only one place
    :param shift: shift with unordered members
    :return: shift with ordered members
    """

    for i, shift_spot in enumerate(shift):
        for member in shift_spot:
            if shift.count(member) > 1:
                shift[i] = shift_spot.remove(member)

    return shift


def member_is_already_assigned_in_shit(shift, member):
    """
    is_not_assigned_in_shit_yet
    :param shift:
    :param member:
    :return:
    """
    is_assigned = False
    for shift_spot in shift:
        for shift_member in shift_spot:
            if isinstance(shift_member, list):
                shift_member = shift_member[0]

            if member == shift_member:
                is_assigned = True
                break

    return is_assigned


def get_qualified_members():
    """
    Create skills members list
    :return: skills
    """
    skills = []
    team_json_data = get_team_json_content()

    for i_skill, _ in enumerate(get_spots(get_places())):

        # List of member for this skill
        list_of_member_for_this_skill = []

        # For each member
        for i_member, member in enumerate(team_json_data['member']):

            # Check if the member has the skill
            if 'X' in team_json_data['member'][i_member]['skills'][i_skill]:

                # Add member for this skill
                list_of_member_for_this_skill.append(team_json_data['member'][i_member]['name'])

            else:
                list_of_member_for_this_skill.append('')

        skills.append(list_of_member_for_this_skill)
    return [skills, skills]


def set_only_one_member_for_a_spot(parsed_shift):
    """
    Set only one member for a spot
    :param parsed_shift: shift before
    :return: shift after
    """
    shift = []
    for shift_spot in parsed_shift:

        if shift_spot is not None and len(shift_spot) > 1:
            shift.append(random.choice(shift_spot))
        elif shift_spot:
            shift.append(shift_spot)

    return shift


def get_spots(places):
    """
    Get spots
    :param places:
    :return: spots
    """

    spots = []
    for spot in places:
        if len(spot) > 0:
            if spot.isdigit():
                spots.append(int(spot))

    spots.sort()
    return spots


if __name__ == '__main__':
    ui.run()
