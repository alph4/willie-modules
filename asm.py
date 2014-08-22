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


@commands('disas', 'disas64', 'disassemble', 'disassemble64')
@example('.disas 66556689e590c9c3')
def disassemble(bot, trigger):
    """Disassemble x86 machine code."""
    if not trigger.group(2):
        return bot.reply('Nothing to disassemble')
    try:
        arg = trigger.group(2)
        # remove all 0x
        while "0x" in arg:
            arg = arg.replace("0x","")
        # remove everything except hex
        arg = re.sub(r"[^a-fA-F0-9]", r"", arg)
        code = unhexlify(arg)
    except Exception:
        return bot.say('Invalid hex sequence')

    bits = 64 if '64' in trigger.group(1) else 32

    filename = '/tmp/' + ''.join( choice(string.ascii_lowercase) for i in range(10)) + '.bin'

    with open(filename, 'wb') as f:
        f.write(code)

    result = Popen(['ndisasm', '-b', str(bits), '-o', '0x1000', filename], stdout=PIPE).stdout.read()

    os.remove(filename)

    for line in result.split('\n'):
        bot.say(line)

@commands('as', 'as64', 'assemble', 'assemble64')
@example('.as push ebp; mov ebp, esp; jmp 0x14')
def assemble(bot, trigger):
    """Assemble x86 instructions."""
    code = trigger.group(2)
    if not code:
        return bot.reply('Nothing to assemble')

    bits = 64 if '64' in trigger.group(1) else 32

    filename = '/tmp/' + ''.join(choice(string.ascii_lowercase) for i in range(10)) + '.asm'

    with open(filename, 'w') as f:
        f.write('BITS %i\n' % bits + re.sub(r';\s*', ';\n', code))

    p = Popen(['nasm', '-f', 'bin', '-o', filename[:-4], filename], stderr=PIPE)
    p.wait()

    os.remove(filename)

    for line in p.stderr.read().split('\n'):
        bot.say(line)

    if p.returncode == 0:
        with open(filename[:-4], 'rb') as f:
            raw = f.read()
            hex = hexlify(raw)
            if hex:
                bot.say(hex)
        os.remove(filename[:-4])

def x86jmp(bot, instr):
    """Display information about a x86 conditional jump."""
    if instr not in jxx:
        return bot.say('I can\'t find anything about that instruction, sorry')

    bot.say('%s : %s' % (instr, jxx[instr]))

def x86instr(bot, instr):
    """Display information about any x86 instruction thats no a conditional jump."""
    raw = web.get('http://www.felixcloutier.com/x86/')

    match = re.search('<tr><td><a href="./(?P<page>[A-Z:]*).html">%s</a></td><td>(?P<desc>[^<]*)</td></tr>' % instr, raw)

    if not match:
        return bot.say('I can\'t find anything about that instruction, sorry')

    bot.say('%s : %s -- %s' % (instr, match.group('desc'), 'http://www.felixcloutier.com/x86/%s' % match.group('page')))

@commands('x86', 'instr', 'instruction')
def instruction(bot, trigger):
    """Display information about an x86 instruction."""
    instr = trigger.group(2)
    if not instr:
        return bot.reply('Give me an instruction')

    instr = instr.strip().upper()
    if 'J' == instr[0] and not instr == 'JMP':
        return x86jmp(bot, instr)

    x86instr(bot, instr)

jxx = {
    'JA'   : 'Jump if above (CF=0 and ZF=0)',
    'JAE'  : 'Jump if above or equal (CF=0)',
    'JB'   : 'Jump if below (CF=1)',
    'JBE'  : 'Jump if below or equal (CF=1 or ZF=1)',
    'JC'   : 'Jump if carry (CF=1)',
    'JCXZ' : 'Jump if CX register is 0',
    'JECXZ': 'Jump if ECX register is 0',
    'JRCXZ': 'Jump if RCX register is 0',
    'JE'   : 'Jump if equal (ZF=1)',
    'JG'   : 'Jump if greater (ZF=0 and SF=OF)',
    'JGE'  : 'Jump if greater or equal (SF=OF)',
    'JL'   : 'Jump if less (SF!=OF)',
    'JLE'  : 'Jump if less or equal (ZF=1 or SF!=OF)',
    'JNA'  : 'Jump if not above (CF=1 or ZF=1)',
    'JNAE' : 'Jump if not above or equal (CF=1)',
    'JNB'  : 'Jump if not below (CF=0)',
    'JNBE' : 'Jump if not below or equal (CF=0 and ZF=0)',
    'JNC'  : 'Jump if not carry (CF=0)',
    'JNE'  : 'Jump if not equal (ZF=0)',
    'JNG'  : 'Jump if not greater (ZF=1 or SF!=OF)',
    'JNGE' : 'Jump if not greater or equal (SF!=OF)',
    'JNL'  : 'Jump if not less (SF=OF)',
    'JNLE' : 'Jump if not less or equal (ZF=0 and SF=OF)',
    'JNO'  : 'Jump if not overflow (OF=0)',
    'JNP'  : 'Jump if not parity (PF=0)',
    'JNS'  : 'Jump if not sign (SF=0)',
    'JNZ'  : 'Jump if not zero (ZF=0)',
    'JO'   : 'Jump if overflow (OF=1)',
    'JP'   : 'Jump if parity (PF=1)',
    'JPE'  : 'Jump if parity even (PF=1)',
    'JPO'  : 'Jump if parity odd (PF=0)',
    'JS'   : 'Jump if sign (SF=1)'
}
