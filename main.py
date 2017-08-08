import yaml
import os.path
import sys
import getopt


class Task(object):
    """
    Represents the task with name and needed skills
    
    >>> data = {'name': 'One', 'skills': ['js', 'python']}
    >>> t = Task(**data)
    >>> t.name 
    'One'
    >>> isinstance(t.skills, list)
    True
    >>> len(t.skills)
    2
    >>> 'js' in t.skills
    True
    >>> t.skills
    ['js', 'python']
    """

    def __init__(self, **kwargs):
        """
        Constructor
        :param kwargs: dictionary with two keys: name and skills. skills should be list of string
        :var kwargs: dict
        """
        self.__name = kwargs.get('name')
        self.__skills = kwargs.get('skills')
        self.__teams = []

    @property
    def name(self):
        return self.__name

    @property
    def skills(self):
        return self.__skills

    @property
    def teams(self):
        return self.__teams

    @staticmethod
    def make_tasks(data):
        """
        Makes list of tasks
        
        :param data: dictionary with key 'Tasks'. Value by this key is list of dictionary. 
        Each dictionary in list should have keys: name and skills. Skills should be list of string
        :return: list of Task
        
        >>> data = {'Tasks': [{'name': 'One', 'skills': ['python', 'postgresql', 'js', 'marketing', 'brand', 'html']}, 
        ...                   {'name': 'Two', 'skills': ['php', 'js', 'mysql', 'html', 'brand']}, 
        ...                   {'name': 'Three', 'skills': ['C++', 'python']}, 
        ...                   {'name': 'Four', 'skills': ['Java', 'Oracle', 'python']}]
        ...        }
        >>> tasks = Task.make_tasks(data)
        >>> isinstance(tasks, list)
        True
        >>> len(tasks)
        4
        >>> isinstance(tasks[0], Task)
        True
        >>> tasks[0].name 
        'One'
        >>> tasks[0].skills
        ['python', 'postgresql', 'js', 'marketing', 'brand', 'html']
        >>> tasks[1].name
        'Two'
        >>> tasks[1].skills
        ['php', 'js', 'mysql', 'html', 'brand']
        >>> tasks[2].name
        'Three'
        >>> tasks[2].skills
        ['C++', 'python']
        >>> tasks[3].name
        'Four'
        >>> tasks[3].skills
        ['Java', 'Oracle', 'python']
        """
        return [Task(**kwargs) for kwargs in data.get('Tasks')]

    def to_dict(self):
        return {'name': self.name,
                'teams': [{'peoples': [p.name for p in t], 'price': sum([p.salary for p in t])} for t in self.teams]}

    @staticmethod
    def to_yaml(tasks):
        return yaml.dump({'Tasks': [t.to_dict() for t in tasks]}, default_flow_style=False)

    @staticmethod
    def save_yaml(tasks, out_file):
        with open(out_file, "w") as f:
            yaml.dump({'Tasks': [t.to_dict() for t in tasks]}, stream=f, default_flow_style=False)

    def make_teams(self, people):
        """
        This method looks for teams using list of people
        
        :param people: list of Person 
        """
        people_have_skills = [p for p in people if set(self.skills) & set(p.skills)]
        teams = []

        # look for people with unique skills for the teams
        skills_count = {s: [] for s in self.skills}
        for p in people_have_skills:
            for skill in self.skills:
                if skill in p.skills:
                    skills_count[skill].append(p)

        people_with_unique_skills = [count[0] for skill, count in skills_count.items() if len(count) == 1]

        def init(curr):  # init list team and team_skills
            t = people_with_unique_skills.copy()
            if curr not in people_with_unique_skills:
                t.append(curr)
            ts = set()
            for p in t:
                ts.update(set(p.skills) & set(self.skills))
            return t, ts

        # make teams
        for current_person in people_have_skills:
            team, teams_skills = init(current_person)

            if teams_skills == set(self.skills):  # they have enough skills for the team
                team.sort()
                if team not in teams:
                    teams.append(team)  # keep sorted for easy remove duplicate teams
                continue

            for other_person in people_have_skills:
                if other_person == current_person or other_person in team:
                    continue

                other_person_skills = set(other_person.skills) & set(self.skills)

                if other_person_skills == set(self.skills):  # he/she has skills the whole team
                    team = [other_person]
                    if team not in teams:
                        teams.append(team.copy())
                    break

                if not other_person_skills.issubset(teams_skills):  # he/she has skills that need for the team
                    teams_skills.update(other_person_skills)
                    team.append(other_person)

                if teams_skills == set(self.skills):  # the team is gathered
                    # remove people with duplicate skills
                    removed = []
                    for i in range(len(team)):  # looking for unnecessary people in the team
                        ts = set()
                        for j in range(len(team)):
                            if i == j:
                                continue
                            ts.update(set(team[j].skills) & set(self.skills))
                        if ts == teams_skills:
                            removed.append(team[i])

                    for r in removed:
                        team.remove(r)  # remove if they don't need
                        ts = set()
                        for p in team:  # checking for need
                            ts.update(set(p.skills) & set(self.skills))
                        if ts != teams_skills:
                            team.append(r)
                    team.sort()
                    if team not in teams:
                        teams.append(team)  # keep sorted for easy remove duplicate teams
                    team, teams_skills = init(current_person)
                    continue

        teams.sort(key=lambda team: sum([person.salary for person in team]))
        self.__teams = teams

    def __str__(self):
        return "Task Name: {}, Needed skills {}".format(self.name, self.skills)

    def __repr__(self):
        return self.__str__()


class Person(object):
    """
    Represents the person that has name, salary and skills
    
    >>> data = {'name': 'Mark', 'salary': 1200, 'skills': ['js', 'python']}
    >>> p = Person(**data)
    >>> p.name
    'Mark'
    >>> p.salary
    1200
    >>> isinstance(p.skills, list)
    True
    >>> len(p.skills)
    2
    >>> 'js' in p.skills
    True
    >>> 'python' in p.skills
    True
    >>> 'ruby' in p.skills
    False
    """

    def __init__(self, **kwargs):
        """
        Constructor
        :param kwargs: dictionary with three keys: name, salary and skills. skills should be list of string       
        :var kwargs: dict
        """
        self.__name = kwargs.get('name')
        self.__salary = kwargs.get('salary')
        self.__skills = kwargs.get('skills')

    @property
    def name(self):
        return self.__name

    @property
    def salary(self):
        return self.__salary

    @property
    def skills(self):
        return self.__skills

    @staticmethod
    def make_people(data):
        """
        Makes list of people

        :param data: dictionary with key 'Peoples'. Value by this key is list of dictionary. 
        Each dictionary in list should have keys: name, salary and skills. Skills should be list of string
        :return: list of Person
        
        >>> data = { 'Peoples': [{'skills': ['js', 'python'], 'salary': 1500, 'name': 'Mark'}, 
        ...                      {'skills': ['js', 'php', 'mysql', 'html'], 'salary': 1200, 'name': 'John'}, 
        ...                      {'skills': ['marketing', 'brand'], 'salary': 1600, 'name': 'Justin'}, 
        ...                      {'skills': ['C++', 'python', 'postgresql'], 'salary': 2500, 'name': 'Petya'}, 
        ...                      {'skills': ['mysql', 'postgresql'], 'salary': 1500, 'name': 'Vasya'}, 
        ...                      {'skills': ['python', 'php', 'marketing'], 'salary': 3500, 'name': 'Stepan'}, 
        ...                      {'skills': ['C++', 'postgresql', 'python'], 'salary': 3000, 'name': 'Vitalya'}, 
        ...                      {'skills': ['php', 'js', 'marketing'], 'salary': 1800, 'name': 'Bryan'}, 
        ...                      {'skills': ['html', 'js'], 'salary': 1800, 'name': 'Voldemar'}]
        ...        }
        >>> people = Person.make_people(data)
        >>> isinstance(people, list)
        True
        >>> len(people)
        9
        >>> isinstance(people[0], Person)
        True
        >>> people[0].name
        'Mark'
        >>> people[0].salary
        1500
        >>> people[0].skills
        ['js', 'python']
        >>> people[8].name
        'Voldemar'
        >>> people[8].salary
        1800
        >>> people[8].skills
        ['html', 'js']
        """
        return [Person(**kwargs) for kwargs in data.get('Peoples')]

    def __gt__(self, other):
        return self.name > other.name

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        return self.name == other.name and self.salary == other.salary and self.skills == other.skills

    def __str__(self):
        return "Person Name: {} Salary: {} Skills: {}".format(self.name, self.salary, self.skills)

    def __repr__(self):
        return self.__str__()


def get_data(yaml_file):
    if not os.path.isfile(yaml_file):
        print("Error: {} is not path to file".format(yaml_file), file=sys.stderr)
    with open(yaml_file) as f:
        return yaml.safe_load(f)


def main(argv):
    input_file = ''
    output_file = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["in=", "out="])
    except getopt.GetoptError:
        print('main.py -i <inputfile> -o <outputfile>', file=sys.stderr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--in"):
            input_file = arg
        elif opt in ("-o", "--out"):
            output_file = arg

    input_file = input_file or os.path.join("test", "task.yaml")
    output_file = output_file or "result.yaml"

    print("Input file {}".format(input_file))
    print("Output file {}".format(output_file))

    data = get_data(input_file)
    tasks = Task.make_tasks(data)
    people = Person.make_people(data)

    for t in tasks:
        t.make_teams(people)

    Task.save_yaml(tasks, output_file)


def test():
    import doctest
    doctest.testmod(verbose=False)

if __name__ == "__main__":
    main(sys.argv[1:])
