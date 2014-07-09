# coding=utf8
"""
nmap.py - Simple Nmap Wrapper Module

Disclaimer: Running nmap against targets on the internet could get you in trouble. Use at your own risk.

(c) 2014 Samuel Groß

http://willie.dftba.net
"""
from __future__ import unicode_literals

from subprocess import Popen, PIPE, call
import socket
import os

from willie.module import commands, example
from willie.config import ConfigurationError

def setup(bot):
    # Check if nmap binary exists
    try:
        call(['nmap', '--version'], stdout=PIPE)     # don't print to stdout
    except OSError:
        raise ConfigurationError('nmap not found in path')

@commands('nmap')
@example('nmap scanme.nmap.org 22')
def nmap(bot, trigger):
    """Perform a basic port scan."""
    try:
        args = trigger.group(2).split(' ', 1)
        target = args[0]
    except:
        return bot.reply('Provide a target.')

    if len(args) > 1:
        ports = args[1]
    else:
        ports = ''

    #
    # Validate target
    #
    try:
        ip = socket.gethostbyname(target)
    except:
        return bot.reply('Invalid hostame or IP address.')

    #
    # Prevent scanning the local network
    #
    if ip[:7] == '192.168' or ip[:3] == '127':
        return bot.reply('Nice try.')

    #
    # Run nmap in a seperate process and get the output
    #
    args = ['nmap', ip, '-T4']
    if ports:
        args += ['-p', ports]
    p = Popen(args, stdout=PIPE, stderr=PIPE)
    p.wait()

    output = p.stdout.read() if p.returncode == 0 else p.stderr.read()

    for line in output.split('\n'):
        if 'Starting nmap' in line:
            continue
        bot.say(line)
