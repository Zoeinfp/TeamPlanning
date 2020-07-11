#!/usr/bin/python
# -*- coding: utf-8 -*
import fileinput
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
    # Places
    places = get_places()

    # Team
    team = get_team()

    # Shift
    shift = get_shift()

    return render_template(template_name_or_list="index.html",
                           team=team,
                           places=places,
                           shift=shift)


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
    :return: void
    """

    # Shift
    shift = get_shift_in_file()

    # Skills
    skills = get_skills()

    for member in shift:

        item_index = shift.index(member)

        if len(skills[item_index]) > 1:

            if member not in skills[item_index]:
                skills[item_index] = "{},{}".format(skills[item_index], member)
        else:
            skills[item_index] = "{}".format(member)

    print("Skills after validation : {}".format(skills))
    empty_skills_file()

    with open("skills.txt", "w", encoding="utf8") as skills_file:
        for i in range(len(skills)):
            skills_file.write("{}={}\n".format(i, skills[i]))

    return jsonify("")


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
    print("Member{}".format(member_name))

    # Member list
    member_list = create_members_list(member_name)

    # Rewrite file for member list
    rewrite_members_after_removing(member_list)
    return jsonify("")


def empty_shift_file():
    """
    Empty shift file
    :return: void
    """
    open("shift.txt", 'w').close()


def empty_skills_file():
    """
    Empty skills file
    :return: void
    """
    open("skills.txt", "w").close()


def get_skills_lines():
    """
    Get skills
    :return: skills
    """
    with open("skills.txt", encoding='utf8') as f:
        skills = f.readlines()
    return skills


def get_table():
    """
    Get table
    :return: places lines
    """
    with open("table.txt", encoding='utf8') as f:
        places_lines = f.readlines()
    return places_lines


def get_team_lines():
    """
    Get team lines
    :return: team lines
    """
    with open("team.txt", encoding='utf8') as f:
        team_lines = f.readlines()
    return team_lines


def get_shift_lines():
    """
    Get shift lines
    :return:
    """
    with open("shift.txt", encoding='utf8') as f:
        places_lines = f.readlines()
    return places_lines


def count_team_member():
    """
    Count team member
    :return:
    """
    count = len(open("team.txt").readlines())
    return count


def get_shift_in_file():
    """
    Get shift in file
    :return: positions for shift
    """
    # Positions
    shift_positions = []
    shift_lines = get_shift_lines()
    for i, line in enumerate(shift_lines):
        shift_positions.append(line.replace("{}=".format(i), "").replace("\n", "").replace(" ", ""))
    return shift_positions


def get_skills():
    """
    Get skills list from file
    :return: skills list
    """
    skills_list = []
    skills = get_skills_lines()
    for i, line in enumerate(skills):
        skills_list.append(line.replace("{}=".format(i), "").replace("\n", ""))
    return skills_list


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
    team_lines = get_team_lines()
    for i, line in enumerate(team_lines):
        team.append(line.replace("{}=".format(i), "").replace("\n", "").replace(" ", ""))
    return team


def get_shift():
    """
    Get shift
    :return: shift
    """

    # Skills list
    skills_list = get_skills()
    print("Skills list {}".format(skills_list))

    # Create shift
    create_shift(skills_list)

    # Get positions for shift
    positions_for_shift = get_shift_in_file()
    return positions_for_shift


def create_members_list(member_name):
    """
    Create members list
    :param member_name:
    :return:
    """
    member_list = []
    members = get_team_lines()
    for i, line in enumerate(members):
        if member_name not in line:
            member_list.append(line.replace("{}=".format(i), "").replace("\n", ""))
    print(member_list)
    return member_list


def rewrite_members_after_removing(member_list):
    """
    Rewrite members after removing
    :param member_list:
    :return: void
    """
    with open("team.txt", "w", encoding='utf8') as f:
        f.write("0=")
        for i, member in enumerate(member_list):
            f.write("{}={}\n".format(i, member.replace("\n", "")))
        f.close()


def write_member_in_team_file(member_name):
    """
    Add member in file
    :param member_name:
    :return:
    """
    count = count_team_member()
    with open("team.txt", "a", encoding="utf8") as team_file:
        team_file.write("\n")
        team_file.write("{}={}".format(str(count), member_name))


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


def create_shift(skills_list):
    """
    Create shift
    :param skills_list:
    :return:
    """
    # Empty shift file
    empty_shift_file()

    # Team
    team = get_team()
    team.remove('')

    # Qualified team
    team, selected_members = get_qualified_team(skills_list, team)

    # Skill list need
    skill_list_need = len(skills_list)

    # Iterator
    iterator = 0

    # While there are some members in team
    while len(team) > 0:

        # Take and test the team member
        selected_member = select_member_in_list(iterator, selected_members)

        while selected_member == '':

            # Choose a random member in team
            selected_member = select_random_member_in_team(team)

            # Add a new member
            # - The choice is greater than 1 (is not empty)
            # - The team member is not already set in the list
            # - The member is in the team
            if len(selected_member) > 1 and selected_member not in selected_members and selected_member in team:
                selected_members[iterator] = selected_member
                team.remove(selected_member)

        iterator += 1

    print("Selected members : {}".format(selected_members))
    with open("shift.txt", "w", encoding='utf8') as f:
        for iterator, member in enumerate(selected_members):
            f.write("{}={}\n".format(iterator, member))


def get_qualified_team(skills_list, team):
    """
    Get qualified member
    :param skills_list: skill list
    :param team: team
    :return: selected members
    """

    # Members
    selected_members = []

    for iterator, member in enumerate(skills_list):

        if iterator == 0:
            selected_member = 'Team Member'
            selected_members.append(selected_member)

        else:

            # If we have a team member ready for the specific place
            if skills_list[iterator] != '':

                # Select team members
                listed_members = skills_list[iterator]

                # Create a list if there is a comma
                listed_members = listed_members.split(",")

                # Choose a member in the list
                selected_member = random.choice(listed_members)

                if selected_member not in selected_members:
                    selected_members.append(selected_member)
                    team.remove(selected_member)
            else:
                selected_members.append('')

    return [team, selected_members]


def select_random_member_in_team(team):
    """
    Select random member in team
    :param team: team
    :return: random team member
    """
    # Choose in team
    selected_member = random.choice(team)
    return selected_member


def select_member_in_list(iterator, selected_members):
    """
    Select member in list
    :param iterator: iterator
    :param selected_members: selected members
    :return: member
    """

    # We take the selected member if exists or set it to empty
    if len(selected_members) >= iterator:
        selected_member = selected_members[iterator]
    else:
        selected_member = ''

    return selected_member


if __name__ == '__main__':
    ui.run()
