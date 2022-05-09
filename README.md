# The bot was created to make your game with your friends in [Jenga](https://en.wikipedia.org/wiki/Jenga) more interesting.

The Telegram Bot is used for the game. Also, you need to have blocks for Jenga. 

[Bot functionality](https://github.com/damagedsystem/JengaQuestsBot/blob/main/main.py) was created with [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI).

This is a portfolio project, but you can try to play it. Just clone the project and edit [quests.txt](https://github.com/damagedsystem/JengaQuestsBot/blob/main/quests.txt) file (1 quest per line, make sure you write down more than 53 lines of quests) and [final.txt](https://github.com/damagedsystem/JengaQuestsBot/blob/main/final.txt) (at least 2 quest).
Don't forget to change Telegram Token with your own one. See [Bots: An introduction for developers](https://core.telegram.org/bots).

For each game, a unique room is created, which you can join by code and play with friends. Each room is created as an instance of the [Room class](https://github.com/damagedsystem/JengaQuestsBot/blob/main/room.py).

***In you want to understand what is going on here, read instructions for game using bot:***

For this game, it is necessary that the blocks were numbered from 1 up to their quantity.
If your blocks are not numbered, just do it with a pencil.

To start the game, someone in your company have to create a room. Once created, the host will receive a room code that all other players have send to the bot in order to join the room.

The number of blocks by default is 54. But host can change it by sending a number of blocks with 'b' letter before numbers. E.g. if you have 60 blocks, just send "b60" to bot.

When all players have joined, you can start the game:

Each player in turn pulls out a block and puts it on top of the tower, as in the standard Jenga game.
Then it's needed to enter  a  block's number in the bot. Each player in the room will receive a description of the quest to be performed by the person who pulled out the block with this number.

Each player takes turns repeating this process until someone will break the tower.
As soon as someone destroys the tower, it's needed to send "end" or just "0" (zero) in the bot. The bot will send the final complicated quest for the person who destroyed the tower.

To leave the room before the end of the game, you can send to bot "leave room" or just "-".
If the current quest is bad / not acceptable, you can send to a bot "random" word or just "/r" and the bot will send another random quest if there is a stock of quests for the game.
Similarly, you can get another final quest by sending "final" or just "/f".
 To get room code: "code" or just "/c".

Enjoy :)
