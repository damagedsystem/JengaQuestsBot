import telebot                  # pyTelegramBotAPI  https://github.com/eternnoir/pyTelegramBotAPI
from telebot import types
import random
from constants import TOKEN     # constants.py file (.gitignore)
# OR  instead of line above write    TOKEN = '*****:*******************'  with your own token inside quotes
from room import Room           # room.py file
from datetime import datetime
import sys


bot = telebot.TeleBot(TOKEN)

# Upload quests for game
quests_file = open('quests.txt')
final_quests_file = open('final.txt')

quests_array, final_quests_array = [], []
for line in quests_file: quests_array.append(line.replace('\n', '').rstrip())
for line in final_quests_file: final_quests_array.append(line.replace('\n', '').rstrip())
quests_file.close()
final_quests_file.close()

rooms = dict()              # When user creates a room then it saves as instance of class "Room"
                            # in variable "rooms" in format {'room_code' : instance_of_class}
                            # e.g. {'g9175': <room.Room object at 0x7fa6ccc49d30>}
                            # or {'g9175': Room g9175} with __repr__ method

user_room_dict = dict()     # Variable for saving current user's room. If user has no room than its value equals ""
                            # Format: {user_id : 'room_code'}
                            # e.g. {111111111 : 'g9175' }
                            # It allows to have access to user's room instance through rooms[user_room_dict[user_chat_id]]


#######################################
# Message handlers
try:
    @bot.message_handler(commands=['start'])            # If command == /start
    def mh_start(msg):
        bot.send_message(msg.chat.id, f"Hello, {msg.chat.first_name}.  Would you start new game or join existing one?"
                                      "\n\nTo see instructions: /instructions",
                         reply_markup=create_new_room_markup())


    @bot.message_handler(commands=['new_game'])   # If command == /new_game
    def mh_new_game(msg):
        bot.send_message(msg.chat.id, "Start new game or join existing one by invitation code?",
                         reply_markup=create_new_room_markup())


    @bot.message_handler(commands=['instructions'])      # If command == /instructions
    def mh_instructions(msg):
        send_instructions(msg.chat.id)


    @bot.message_handler(content_types=['text'])        # If user sent text
    def mh_text(msg):
        bot_text_processing(msg)
except Exception as e:
    print(e)
#######################################


#######################################
# Markups
def create_new_room_markup():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    new_game_b= types.KeyboardButton('create new room')
    join_game_b = types.KeyboardButton('join an existing room')
    return markup.row(new_game_b, join_game_b)


def new_game_inside_room_markup():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    play_again_b= types.KeyboardButton('play again')
    leave_room_b = types.KeyboardButton('leave room')
    return markup.row(play_again_b, leave_room_b)
#######################################


# Processing of a text from user sent to bot
def bot_text_processing(msg):
    global rooms, user_room_dict

    text = msg.text.lower().replace('"','') # The whole text is processed in lowercase
    chat_id = msg.chat.id                   # Chat_id of user who sent text
    username = msg.chat.first_name          # username of user who sent text

    if chat_id not in user_room_dict: # If user is not inside any room than its room value in dict is empty
        user_room_dict[chat_id] = ""

    try: # Prevent the bot from stopping due to an error
        if text == "create new room":
            try:
                if user_room_dict[chat_id] != "":  # If user already in other room, then user leaves previous one.
                    leave_room(chat_id, username, joined=True)
                # Trying to execute create_room() function, which creates a room and
                # returns game identifier (room code, e.g. 'g9175')
                bot.reply_to(msg, text=f"New room created.\nTell this code to your friends if"
                                       f" you want them to join:\n\n{create_room(chat_id, username)}"
                                       f"\n\nNumber of blocks by default is 54. If you have another quantity of blocks,"
                                       f" you can change this value.\n"
                                       f"For more information you can see /instructions")
            except Exception as error:
                print(error)
                bot.reply_to(msg, text="Sorry, something went wrong. Try again, please")

        elif text == "join an existing room":
            bot.reply_to(msg, text="Please, enter room code in following format: \n\n g0000\n\n with your host's numbers "
                                   "instead of zeroes"
                                   f"\n\nInstructions for game: /instructions")
        elif text[0] == 'g' and text[1:].isdigit(): # To connect to room need to send code in format 'g0000'
                                                    # with room four numbers instead of zeroes
            if len(text[1:]) == 4:
                if user_room_dict[chat_id] == text:
                    bot.reply_to(msg, text="You are in this room already!")
                elif text not in rooms:
                    bot.reply_to(msg, text="There are no such room. Please, try again or create new room")
                else: # If user not in this room already and this room exist:
                    if user_room_dict[chat_id] != "": # If user already in other room, then user leaves previous one.
                        leave_room(chat_id, username, joined=True)
                    bot.reply_to(msg, text=join_room(chat_id, username, text))
                    all_players = get_all_users_inside_room(chat_id)    # Function returns all users from current room
                                                                        # in format {user_id: username} for each one
                    players = current_players(chat_id)      # Function returns text in format:
                                                            # Current players (num_of_players): comma_separated_names
                                                            # e.g. "Current players (3): User1, User2, User3"
                    for user in all_players:    # Send message to all users inside room
                        bot.send_message(user, text=f"New user {username} joined the room.\n"
                                                    f"{players}")
            else:
                bot.reply_to(msg, text="If you want to connect to room please send message in following format: \n\n"
                                       "g0000\n\n"
                                       "with your host's room numbers instead of zeroes.")
        elif user_room_dict[chat_id] != "": # If user in some room:
            if text == "play again":
                if is_host(chat_id): # If the user is host:
                    play_again(chat_id) # This function shuffles all quests inside room for new game
                    all_players = get_all_users_inside_room(chat_id)
                    players = current_players(chat_id)
                    for user in all_players:
                        bot.send_message(user, text=f'New game started.\n'
                                                    f"{players}")
                else: # If user isn't host
                    bot.reply_to(msg, text="Please, wait for your host's command")
            elif text in ['leave room', '-']:
                leave_room(chat_id, username)   # If user is host all leave room, otherwise only one user leaving room and
                                                # other receive messages about user leaving
            elif text in ['/r', 'random']:    # If current quest is bad, users can receive another random one from reserve.
                                             # If there are 60 quests in database and 54 blocks for game than reserve
                                             # equals to 6 questions.
                for user in get_all_users_inside_room(chat_id):
                    bot.send_message(user, text=get_another_quest(chat_id))
            elif text in ['/f', 'final']: # Get another quest for person who made the tower fall if current quest is bad
                for user in get_all_users_inside_room(chat_id):
                    bot.send_message(user, text=get_another_final_uqest(chat_id),
                                     reply_markup=new_game_inside_room_markup())
            elif text in ['0', 'end']: # Send final quest for person who made the tower fall
                for user in get_all_users_inside_room(chat_id):
                    bot.send_message(user, text=f"Final quest: {get_final_quest(chat_id)}",
                                     reply_markup=new_game_inside_room_markup())
            elif text in ['/c', 'code']: # Get current room code, if user want it to see (e.g. to invite friend)
                bot.reply_to(msg, text=f'Room code: {user_room_dict[chat_id]}')
            elif text[0] == 'b' and text[1:].isdigit(): # Number of blocks by default is 54, but host can change it
                if is_host(chat_id):
                    message, success = change_num_of_blocks(chat_id, int(text[1:]))
                    if success: # Send message with new quantity of blocks to all users inside room
                        for user in get_all_users_inside_room(chat_id):
                            bot.send_message(user, text=message)
                    else: # Send message to host why can't change quantity of blocks
                        bot.reply_to(msg, text=message)
                else:
                    bot.reply_to(msg, text="Sorry, only host can change the number of blocks")
            elif text.isdigit(): # If text is number
                text = int(text)
                if user_room_dict[chat_id] == "": # Send invitation if user not in any room
                    not_in_any_room(chat_id)
                else:
                    # Block's number processing
                    if text in range(1, get_quantity_of_blocks(chat_id)+1):
                        for user in get_all_users_inside_room(chat_id):
                            bot.send_message(user, f"Quest: {get_quest(chat_id, text)}") # Send quest by number
                    else:
                        bot.reply_to(msg, text=f"Please, enter number in range between 1"
                                               f" and {get_quantity_of_blocks(chat_id)}")
            else:
                bot.reply_to(msg, text="Sorry, unknown command.")

        else: # If user not in any room
            not_in_any_room(chat_id)   # Send create_new_room_markup to user
    except Exception as err: # Write logs into file if error
        _, _, exc_tb = sys.exc_info()
        with open('logs.txt', 'a+') as f:
                # Save logs in format "_data_ _time_ Error(line _line_number_): _error_text_"
                # e.g. 08/05/2022 13:04:58 Error(line 100): invalid literal for int() with base 10: 'some text'
                f.writelines(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + f' Error(line {exc_tb.tb_lineno}): ' + str(err) + '\n\n')
        bot.reply_to(msg, text="Sorry, something went wrong. An error message has been sent to the developer.\nIt'll be fixed as soon as possible")

def create_room(chat_id, username):
    global quests_array, final_quests_array, rooms, user_room_dict
    # Get unique game identifier (room code)
    game_identifier = 'g' + str(random.randint(1000, 9999))
    while game_identifier in rooms:
        game_identifier = 'g' + str(random.randint(1000, 9999))
    # Get quests for room
    quests = quests_array.copy()
    final_q = final_quests_array.copy()
    random.shuffle(quests)
    random.shuffle(final_q)
    # Create an instance of Room's class
    locals()[game_identifier] = Room(chat_id, username, quests, final_q, game_identifier)
    # Add new room to rooms variable in format {'game_identifier' : room's_instance}
    rooms[game_identifier] =(locals()[game_identifier])
    # Add current room identifier to host in user_room_dict
    user_room_dict[chat_id] = game_identifier
    return game_identifier


def join_room(chat_id, username, room_id):
    global rooms, user_room_dict
    # Add user's chat_id and username to instance of current room
    rooms[room_id].join_room(user_id=chat_id, username=username)
    # Add current room identifier to user in user_room_dict
    user_room_dict[chat_id] = room_id
    return "You successfully joined the room."


def not_in_any_room(my_id):
    bot.send_message(my_id, text='You are not in any game right now.')
    bot.send_message(my_id,text='Do want want to create a game or join existing one (given by your host)?',
                     reply_markup=create_new_room_markup())


def get_all_users_inside_room(chat_id):
    global rooms, user_room_dict
    # Return all users and its usernames inside room as dict
    return rooms[user_room_dict[chat_id]].users


def get_quantity_of_blocks(chat_id):
    global rooms, user_room_dict
    # Return current quantity of blocks
    return rooms[user_room_dict[chat_id]].num_of_blocks


def get_quest(chat_id, text):
    global rooms, user_room_dict
    # Return quest by number
    return rooms[user_room_dict[chat_id]].quests[int(text)-1]


def play_again(chat_id):
    global rooms, user_room_dict
    # Shuffle all quests inside room
    return rooms[user_room_dict[chat_id]].shuffle_quests()


def leave_room(chat_id, username, joined=False):
    global rooms, user_room_dict
    users = get_all_users_inside_room(chat_id).copy()
    room_code = user_room_dict[chat_id]
    # If user is host than all leave room
    if is_host(chat_id):
        room_id = user_room_dict[chat_id]
        for user in users:
            bot.send_message(user, f"Game {room_code} over.")
            if joined: # Host not receive send_create_room_markup if connect to new room
                if not is_host(user):
                    send_create_room_markup(user)
            else:
                send_create_room_markup(user) # All other users receive send_create_room_markup
            user_room_dict[user] = ""
        del rooms[room_id]
    else: # Only current user leaves room
        rooms[user_room_dict[chat_id]].remove_user(chat_id)
        for user in users:
            host_id = rooms[user_room_dict[chat_id]].host_id
            if user != chat_id: # Inform rest users about action
                bot.send_message(user, text=f"User {username} left the game. {current_players(host_id)}")
            else:
                bot.send_message(user, text=f"You left the game. ")
        user_room_dict[chat_id] = ""
        send_create_room_markup(chat_id)


def is_host(chat_id):
    global rooms, user_room_dict
    return rooms[user_room_dict[chat_id]].host_id == chat_id


def get_final_quest(chat_id):
    global rooms, user_room_dict
    return rooms[user_room_dict[chat_id]].final_quests[0]


def current_players(chat_id):
    global rooms, user_room_dict
    # Function returns text in format:
    # Current players (num_of_players): comma_separated_names
    # e.g. "Current players (3): User1, User2, User3"
    return rooms[user_room_dict[chat_id]].players()


def get_another_quest(chat_id):
    global rooms, user_room_dict
    # If current quest is bad, users can receive another random one from reserve.
    # If there are 60 quests in database and 54 blocks for game than reserve
    # equals to 6 questions.
    return rooms[user_room_dict[chat_id]].get_another_quest()


def get_another_final_uqest(chat_id):
    global rooms, user_room_dict
    # Return another quest for person who made the tower fall if current quest is bad
    return rooms[user_room_dict[chat_id]].get_another_final_quest()


def change_num_of_blocks(chat_id, num):
    global rooms, user_room_dict
    # Change number of blocks for game to num
    return rooms[user_room_dict[chat_id]].change_num_of_blocks(num)


def send_create_room_markup(chat_id):
    bot.send_message(chat_id, text='Do want want to create a game or join existing one (given by your host)?',
                     reply_markup=create_new_room_markup())


def send_instructions(chat_id):
    block_1 = "The bot was created to make your Jenga game with friends more interesting.\n\n" \
              "For this game, it is necessary that the blocks were numbered from 1 up to their quantity.\n" \
              "If your blocks are not numbered, just do it with a pencil.\n\n" \
              "To start the game, someone in your company have to create a room. Once created, the host will receive " \
              "a room code that all other players have send to the bot in order to join the room.\n\n" \
              "The number of blocks by default is 54. But host can change it by sending a number of blocks " \
              "with 'b' letter before numbers. " \
              "E.g. if you have 60 blocks, just send \"b60\" to bot."

    block_2 = "When all players have joined, you can start the game:\n\n" \
              "Each player in turn pulls out a block and puts it on top of the tower, as in the standard Jenga game.\n" \
              "Then it's needed to enter  a  block's number in the bot. " \
              "Each player in the room will receive a description of the quest to be performed by the person " \
              "who pulled out the block with this number.\n\n" \
              "Each player takes turns repeating this process until someone will break the tower.\n" \
              "As soon as someone destroys the tower, it's needed to send \"end\" or just \"0\" (zero) in the bot. " \
              "The bot will send the final complicated quest for the person who destroyed the tower."

    block_3 = "To leave the room before the end of the game, you can send to bot \"leave room\" or just \"-\".\n" \
              "If the current quest is bad / not acceptable, you can send to a bot \"random\" word or just \"/r\" " \
              "and the bot will send another random quest if there is a stock of quests for the game.\n" \
              "Similarly, you can get another final quest by sending \"final\" or just \"/f\".\n" \
              " To get room code: \"code\" or just \"/c\".\n\nEnjoy :)"

    for block in block_1, block_2, block_3:
        bot.send_message(chat_id, text=block, reply_markup=create_new_room_markup())


print("The bot is running")
bot.polling()
