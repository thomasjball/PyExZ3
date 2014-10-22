# Configuration
INSTALLDIR=/home/vagrant/pyex

# System Maintenance 
apt-get update
apt-get -y upgrade

## Modern Git
apt-get -y install git
apt-get -y install zlib1g-dev libcurl4-openssl-dev
apt-get -y install autoconf
cd /tmp
git clone https://github.com/git/git.git 
cd git
make configure
./configure --prefix=/usr
make all
make install
cd

# Dependencies
apt-get -y install python3
apt-get -y install graphviz graphviz-dev

## Z3
apt-get -y install g++
apt-get -y install python3-examples
cd /tmp
git clone https://git01.codeplex.com/z3
cd z3
git checkout -b unstable origin/unstable
python scripts/mk_make.py
cd build
make
make install
cp libz3.so /usr/lib/python3/dist-packages
python3 /usr/share/doc/python3.2/examples/scripts/reindent.py z3*.py
cp z3*.py /usr/lib/python3/dist-packages
cp z3*.pyc /usr/lib/python3/dist-packages
cd

# Installation
ln -s /vagrant $INSTALLDIR

# Tests
cd $INSTALLDIR
python3 run_tests.py test
python3 run_tests.py fail    
