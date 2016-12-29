#!/bin/sh
. /usr/local/bin/aws_bash_completer
umask 0077

PYTHONDONTWRITEBYTECODE=1
export PYTHONDONTWRITEBYTECODE

HISTCONTROL=ignoreboth
export HISTCONTROL

HISTSIZE=8192
export HISTSIZE

PAGER=more
export PAGER

EDITOR=/usr/bin/vi
export EDITOR

PATH=${PATH}:/aws/bin:/aws/sbin
export PATH

PYTHONPATH=/aws
export PYTHONPATH

