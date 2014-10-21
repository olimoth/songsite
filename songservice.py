import datetime
import flask
import os
import songmaker


app = flask.Flask(__name__)
song_writer = None

WORD_POOL_SIZE = 50000
MIN_LETTERS = 4
MAX_LETTERS = 9


def main():
    global song_writer
    text_path = os.path.join(os.path.dirname(__file__), 'metamorphosis.txt')
    reader = songmaker.Reader(open(text_path, 'r'))
    reader.parse_text()
    generator = songmaker.WordGenerator(
        reader,
        min_letters=MIN_LETTERS, 
        max_letters=MAX_LETTERS, 
        allow_doubles=False)
    loads_of_words = [generator.generate_word() for i in range(WORD_POOL_SIZE)]
    song_writer = songmaker.SongWriter(loads_of_words)

@app.route("/")
def get_song():
    scheme = flask.request.args.get('scheme')
    min_syllables = int(flask.request.args.get('minSyllables', 1))
    max_syllables = int(flask.request.args.get('maxSyllables', 4))
    print '{} | min: {}, max: {}, scheme: {}'.format(
        datetime.datetime.now(), min_syllables, max_syllables, scheme)
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
    main()
    print 'ready'
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
