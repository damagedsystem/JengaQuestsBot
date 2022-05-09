import random


class Room():
    def __init__(self, host_id, host_name, quests, final_quests, game_identifier):
        self.host_id = host_id
        self.users = {host_id: host_name}
        self.quests = quests
        self.final_quests = final_quests
        self.game_identifier = game_identifier
        self.num_of_blocks = 54


    def __repr__(self):
        return f"Room {self.game_identifier}"


    def join_room(self, user_id, username):
        self.users[user_id] = username


    def shuffle_quests(self):
        random.shuffle(self.quests)
        random.shuffle(self.final_quests)


    def remove_user(self, user):
            del self.users[user]


    def players(self):
        return  f"Current players({len(self.users)}): {', '.join(self.users.values())}"


    def get_another_quest(self):
        if len(self.quests) > self.num_of_blocks:
            rest = self.quests[self.num_of_blocks+1:]
            return f"Random quest:\n{rest[random.randint(0, len(rest)-1)]}\n\n" \
                   f"Random quests available: {len(rest)}." if rest else "Sorry, there are no more quests"
        else:
            return "Sorry, there are no more quests"


    def get_another_final_quest(self):
        if len(self.final_quests) == 1:
            return "Sorry, there are no more quests"
        else:
            first_el = self.final_quests.pop(0)
            self.final_quests.append(first_el)
            return f"Another final quest:\n{self.final_quests[0]}"


    def change_num_of_blocks(self, num):
        if num < 12:
            return "The number of blocks for game is too small.", False
        else:
            if len(self.quests) < num:
                return f"Sorry, there are only {len(self.quests)} quests in database.", False
            else:
                self.num_of_blocks = num
                return f"Number of blocks was successfully set to {num}", True