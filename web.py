import flask
import songmaker


app = flask.Flask(__name__)

WORD_POOL_SIZE = 50000
MIN_LETTERS = 4
MAX_LETTERS = 9


@app.route("/song")
def get_song():
    return 'here is a song lol'


if __name__ == "__main__":
    reader = Reader(open('eightydays.txt', 'r'))
    reader.parse_text()
    generator = WordGenerator(
        reader,
        min_letters=MIN_LETTERS, 
        max_letters=MAX_LETTERS, 
        allow_doubles=False)
    loads_of_words = [generator.generate_word() for i in range(WORD_POOL_SIZE)]
    song_writer = SongWriter(loads_of_words, args.rhyming_scheme)

    app.run(debug=True)
