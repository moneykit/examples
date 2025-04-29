FROM ruby:3.4.3

WORKDIR /app

COPY ./Gemfile ./Gemfile.lock /app/
RUN bundle install

COPY . /app

ENV PORT=8000
EXPOSE 8000

CMD ["bundle", "exec", "ruby", "app.rb"]
