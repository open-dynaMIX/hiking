FROM python:3.11-slim

ENV APP_HOME=/app

#RUN mkdir -p $APP_HOME && apt-get update && \
#    apt-get install -y --no-install-recommends wget unzip gcc && \
#    wget https://www.sqlite.org/2024/sqlite-autoconf-3450100.tar.gz && \
#    tar xvfz sqlite-autoconf-3450100.tar.gz && \
#    cd sqlite-autoconf-3380500 && \
#    export CFLAGS="-DSQLITE_ENABLE_FTS3 \
#    -DSQLITE_ENABLE_FTS3_PARENTHESIS \
#    -DSQLITE_ENABLE_FTS4 \
#    -DSQLITE_ENABLE_FTS5 \
#    -DSQLITE_ENABLE_JSON1 \
#    -DSQLITE_ENABLE_LOAD_EXTENSION \
#    -DSQLITE_ENABLE_RTREE \
#    -DSQLITE_ENABLE_STAT4 \
#    -DSQLITE_ENABLE_UPDATE_DELETE_LIMIT \
#    -DSQLITE_SOUNDEX \
#    -DSQLITE_TEMP_STORE=3 \
#    -DSQLITE_USE_URI \
#    -O2 \
#    -fPIC" && \
#    export PREFIX="/usr/local" && \
#    LIBS="-lm" ./configure --disable-tcl --enable-shared --enable-tempstore=always --prefix="$PREFIX" && \
#    make && \
#    make install && \
#    pip install poetry

WORKDIR $APP_HOME
COPY . $APP_HOME

#COPY pyproject.toml poetry.lock $APP_HOME/
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget unzip build-essential && \
    wget "https://sqlite.org/2024/sqlite-amalgamation-3450200.zip" -P /tmp/sqlite3 && \
    unzip /tmp/sqlite3/sqlite-amalgamation-3450200.zip -d /tmp/sqlite3 && \
    mkdir -p /opt/sqlite3 && \
    gcc -shared -o /opt/sqlite3/libsqlite3.so -fPIC /tmp/sqlite3/sqlite-amalgamation-3450200/sqlite3.c && \
    pip install poetry && \
    poetry install

#RUN  ls -la sqlite3 && \
#     cd $APP_HOME/sqlite3/sqlite-amalgamation-3450200/ && \
#     pwd && \
#     gcc -shared -o $APP_HOME/sqlite3/libsqlite3.so -fPIC $APP_HOME/sqlite3/sqlite-amalgamation-3450200/sqlite3.c
##    # this uses malloc_usable_size, which is incompatible with fortification level 3
##    export CFLAGS="$CFLAGS/_FORTIFY_SOURCE=3/_FORTIFY_SOURCE=2" && \
##    export CXXFLAGS="$CXXFLAGS/_FORTIFY_SOURCE=3/_FORTIFY_SOURCE=2" && \
##    export CPPFLAGS="$CPPFLAGS \
##          -DSQLITE_ENABLE_COLUMN_METADATA=1 \
##          -DSQLITE_ENABLE_UNLOCK_NOTIFY \
##          -DSQLITE_ENABLE_DBSTAT_VTAB=1 \
##          -DSQLITE_ENABLE_FTS3_TOKENIZER=1 \
##          -DSQLITE_ENABLE_FTS3_PARENTHESIS \
##          -DSQLITE_SECURE_DELETE \
##          -DSQLITE_ENABLE_STMTVTAB \
##          -DSQLITE_ENABLE_STAT4 \
##          -DSQLITE_MAX_VARIABLE_NUMBER=250000 \
##          -DSQLITE_MAX_EXPR_DEPTH=10000 \
##          -DSQLITE_ENABLE_MATH_FUNCTIONS"
#
##RUN ls -la && \
##    cd sqlite-src-3450200 && \
##    ./configure --prefix=/usr \
##  	--disable-static \
##  	--enable-fts3 \
##  	--enable-fts4 \
##  	--enable-fts5 \
##  	--enable-rtree \
##  	TCLLIBDIR=/usr/lib/sqlite3.45.2 || cat ./config.log && \
##    sed -i -e 's/ -shared / -Wl,-O1,--as-needed\0/g' libtool && \
##    make && \
##    make DESTDIR="$APP_HOME/sqlite3" install
#
#
#WORKDIR $APP_HOME
#
##RUN wget "https://www.sqlite.org/2024/sqlite-tools-linux-x64-3450100.zip" -P /tmp && \
##    unzip "/tmp/$(basename 'https://www.sqlite.org/2024/sqlite-tools-linux-x64-3450100.zip')" -d /tmp && \
##    install /tmp/sqlite3 /usr/local/bin/ && \
##    pip install poetry
#
#RUN pip install poetry && \
#    poetry install
#
##COPY . $APP_HOME
#
ENV LD_LIBRARY_PATH=/opt/sqlite3
#
CMD poetry run pytest -vv ./hiking