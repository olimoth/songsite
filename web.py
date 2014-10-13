import flask
import songmaker


app = flask.Flask(__name__)

WORD_POOL_SIZE = 10000
MIN_LETTERS = 4
MAX_LETTERS = 9


@app.route("/song")
def get_song():
    scheme = flask.request.args.get('scheme')
    while True:
        try:
            song = song_writer.get_song(scheme)
            return flask.jsonify({'songlines': song})
        except IndexError:
            continue


if __name__ == "__main__":
    reader = songmaker.Reader(open('eightydays.txt', 'r'))
    reader.parse_text()
    generator = songmaker.WordGenerator(
        reader,
        min_letters=MIN_LETTERS, 
        max_letters=MAX_LETTERS, 
        allow_doubles=False)
    loads_of_words = [generator.generate_word() for i in range(WORD_POOL_SIZE)]
    song_writer = songmaker.SongWriter(loads_of_words)

    print 'ready'

    app.run(debug=True)
