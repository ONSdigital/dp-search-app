curl -OL http://ftpmirror.gnu.org/libtool/libtool-2.4.2.tar.gz
tar -xzf libtool-2.4.2.tar.gz
cd libtool-2.4.2
./configure && make && sudo make install

# brew install 'https://raw.github.com/simonair/homebrew-dupes/e5177ef4fc82ae5246842e5a544124722c9e975b/ab.rb'
# brew test ab

curl -O https://archive.apache.org/dist/httpd/httpd-2.4.2.tar.bz2
tar zxvf httpd-2.4.2.tar.bz2
cd httpd-2.4.2.tar.bz2
./configure && make && make install

