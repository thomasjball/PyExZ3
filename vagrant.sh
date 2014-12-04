# Configuration
INSTALLDIR=/home/vagrant/pyex

# System Maintenance 
apt-get update
apt-get -y upgrade

## Modern Git
apt-get -y install git
apt-get -y install gettext zlib1g-dev libcurl4-openssl-dev
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

## CVC4
apt-get install -y libgmp-dev
apt-get install -y libboost-all-dev
apt-get install -y openjdk-7-jre openjdk-7-jdk
apt-get install -y swig
cd /tmp
git clone https://github.com/CVC4/CVC4.git
cd CVC4
./autogen.sh
contrib/get-antlr-3.4
export PYTHON_CONFIG=/usr/bin/python3.2-config
./configure --with-antlr-dir=/tmp/CVC4/antlr-3.4 ANTLR=/tmp/CVC4/antlr-3.4/bin/antlr3 --enable-language-bindings=python
echo "python_cpp_SWIGFLAGS = -py3" >> src/bindings/Makefile.am
autoreconf
make
make doc
make install
echo "/usr/local/lib" > /etc/ld.so.conf.d/cvc4.conf
cp builds/src/bindings/python/CVC4.py /usr/lib/python3/dist-packages/CVC4.py
cp builds/src/bindings/python/.libs/CVC4.so /usr/lib/python3/dist-packages/_CVC4.so
cd

# Installation
ln -s /vagrant $INSTALLDIR

# Tests
cd $INSTALLDIR
python3 run_tests.py test
