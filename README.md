# MF-Bot

**Welcome to the MF-Bot documentation!**

If you read this, you were promoted to MFBot-Coder, so please read there rules

1. Even though most of problems are solved democratically, De'Max is able to make important choices himself

2. Respect people's privacy and don't speak to people you found in bot's database
and don't enter chats you found in bot's database. Except you found them somewhere else


**How to create a new command:**

1. First of all, think, where should you place logic for your command:

**start.py** if your command relates to /start command

**elite.py** if your command if related to elite testing

**complicated_commands.py** if your command involves creating inline-buttons

**developer_commands.py** if your command is useless for users but useful for developers

**reactions.py** if your command triggers not by /command but by some event like new user or some trigger in the text

**boss_commands.py** if your command requires some special permissions for a person who tries to use your command

**standart_commands.py** if your command hasn't some special properties like other ones


>*if your command relates to two or more groups, then choose the highest group of them*


2. Make sure you checked functions in **config**, they might be useful for you, if there you need a function that isn't there, just make it yourself

3. Also check **output.py**

4. After you done with the logic, create a handler in **input.py**. Your
handler have to be near handlers of function with the same type (like boss_commands)
Name handler like *command_name*_handler. Fill your handler with some checks, like:

**in_mf** necessary function. Also fill parameter command_type with:

*'standart_commands'* if your command is for fun

*'boss_commands'* if your command is for admins

*'financial_commands'* if your command is for financial system

*None* if nothing of that


**is_suitable** if person must have some permissions in a chat. Fill pararam comand_type with:

*'standart'* if person simply isn't banned

*'advanced'* if person is something between admin and member. Like MF-2 citizen

*'boss'* if it's some admin stuff like banning of warning

*'uber'* if it's some uber-admin stuff like promoting and demoting admins

*'chat_changer'* if it's something so important that only leader and their deputy(s) can do.
Like (de)activating money system or adding new chats to a system


**cooldown** if there must be a pause between two usages of a same command by a same person

5. Make sure you use LOG to log invoking command and it's handler

6. Check your code with Pylint. If there are complaints, fix them

7. Commit your changes and push them. Your commit text have to look like:


type(scope): description

>type can be:

**feat** new feature

**fix** bug fix

**refactor** changes in code structure

**docs** documentation changes

**revert** reverting previous commit

**todos** new TODOs

>scope is unnecessary and can be like:

**money_system**, **storage**

>description is simply a description written in human language

8. After all of that you should be proud of yourself. You did a great job! :-)

>*This documentation will be updated so please keep up with commits other people do*
