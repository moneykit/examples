FROM ruby:3.2.2

WORKDIR /app

COPY ./Gemfile ./Gemfile.lock /app/
RUN bundle install

COPY . /app

ENTRYPOINT [ "bash" ]
CMD ["./run.sh"]
