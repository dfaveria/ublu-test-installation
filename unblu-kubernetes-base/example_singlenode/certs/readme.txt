# You must concatenate the ca-bundle and crt files to a single crt file like:

cat /usr/local/etc/ssl.crt/star_example_com.crt > tls.crt
cat /usr/local/etc/ssl.crt/star_example_com.ca-bundle >> tls.crt
