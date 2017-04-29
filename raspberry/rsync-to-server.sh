#!/bin/sh

rsync -a --remove-source-files /tmp/*npy tunnelgott@cress.shack:store/`hostname`/
