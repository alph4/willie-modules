# coding=utf8
"""
asm.py - (dis)assembly features.

(c) 2014 Samuel Groß
"""
from willie import web
from willie.module import commands, nickname_commands, example

from random import choice
from binascii import hexlify, unhexlify
import string
import re
import os
from subprocess import Popen, PIPE


@commands('disas', 'disassemble')
@nickname_commands('disas', 'disassemble')
@example('.disas 66556689e590c9c3')
def disassemble(bot, trigger):
    """Disassemble Intel X86 machine code."""
    if not trigger.group(2):
        return bot.reply('Nothing to disassemble')
    try:
        code = unhexlify(trigger.group(2))
    except Exception:
        return bot.say('Invalid hex sequence')

    filename = '/tmp/' + ''.join( choice(string.ascii_lowercase) for i in range(10)) + '.bin'

    with open(filename, 'wb') as f:
        f.write(code)

    result = Popen(['ndisasm', '-b', '32', '-o', '0x1000', filename], stdout=PIPE).stdout.read()

    os.remove(filename)

    for line in result.split('\n'):
        bot.say(line)

@commands('as', 'assemble')
@nickname_commands('as', 'assemble')
@example('.as push ebp; mov ebp, esp; jmp 0x14')
def assemble(bot, trigger):
    """Assemble Intel X86 instructions."""
    code = trigger.group(2)
    if not code:
        return bot.reply('Nothing to assemble')

    filename = '/tmp/' + ''.join(choice(string.ascii_lowercase) for i in range(10)) + '.asm'

    with open(filename, 'w') as f:
        f.write('BITS 32\n' + re.sub(r';\s*', ';\n', code))

    p = Popen(['nasm', '-f', 'bin', '-o', filename[:-4], filename])
    p.wait()

    os.remove(filename)

    if p.returncode == 0:
        with open(filename[:-4], 'rb') as f:
            raw = f.read()
            hex = hexlify(raw)
            if hex:
                bot.say(hex)
            else:
                bot.say('Sorry, can\'t assemble that')
        os.remove(filename[:-4])
    else:
        bot.say('Sorry, can\'t assemble that')
