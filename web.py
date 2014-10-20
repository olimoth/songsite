import flask
import songmaker


app = flask.Flask(__name__)

WORD_POOL_SIZE = 50000
MIN_LETTERS = 4
MAX_LETTERS = 9


@app.route("/song")
def get_song():
    scheme = flask.request.args.get('scheme')
    min_syllables = int(flask.request.args.get('minSyllables', 1))
    max_syllables = int(flask.request.args.get('maxSyllables', 4))
    while True:
        try:
            song = song_writer.get_song(scheme, min_syllables, max_syllables)
            resp = flask.make_response(flask.jsonify({'songlines': song}))
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
        except IndexError:
            continue
        except songmaker.NoValidRhymeGroupsFound:
            resp = flask.make_response(flask.jsonify(
                {'songlines': ['could not create a song with those parameters']}))
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp


if __name__ == "__main__":
    reader = songmaker.Reader(open('metamorphosis.txt', 'r'))
    reader.parse_text()
    generator = songmaker.WordGenerator(
        reader,
        min_letters=MIN_LETTERS, 
        max_letters=MAX_LETTERS, 
        allow_doubles=False)
    loads_of_words = [generator.generate_word() for i in range(WORD_POOL_SIZE)]
    song_writer = songmaker.SongWriter(loads_of_words)

    print 'ready'

    app.run(host='0.0.0.0', debug=True, use_reloader=False)
