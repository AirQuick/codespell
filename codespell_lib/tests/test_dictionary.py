# -*- coding: utf-8 -*-

import aspell
import os.path as op
import re
import warnings


def test_dictionary_formatting():
    """Test that all dictionary entries are valid."""
    speller = aspell.Speller('lang', 'en')
    err_dict = dict()
    ws = re.compile(r'.*\s.*')  # whitespace
    comma = re.compile(r'.*,.*')  # comma
    with open(op.join(op.dirname(__file__), '..', 'data',
                      'dictionary.txt'), 'rb') as fid:
        for line in fid:
            err, rep = line.decode('utf-8').split('->')
            err = err.lower()
            assert err != rep, 'error %r corrects to itself' % err
            assert err not in err_dict, 'error %r already exists' % err
            assert ws.match(err) is None, 'error %r has whitespace' % err
            assert comma.match(err) is None, 'error %r has a comma' % err
            warnings.warn(speller.ConfigKeys()['encoding'][2])
            #if not speller.check(
            #        err.encode(speller.ConfigKeys()['encoding'][2])):
            #    warnings.warn(('warning %r is in the aspell dictionary'
            #                   % err), UserWarning)
            # assert err not in speller, ('error %r is in the aspell dictionary'
            #                             % err)
            rep = rep.rstrip('\n')
            assert len(rep) > 0, ('error %s: correction %r must be non-empty'
                                  % (err, rep))
            assert not re.match(r'^\s.*', rep), ('error %s: correction %r '
                                                 'cannot start with whitespace'
                                                 % (err, rep))
            for (r, msg) in [
                (r'^,', 'error %s: correction %r starts with a comma'),
                (r'\s,', 'error %s: correction %r contains a whitespace '
                         'character followed by a comma'),
                (r',\s\s', 'error %s: correction %r contains a comma followed '
                           'by multiple whitespace characters'),
                (r',[^ ]', 'error %s: correction %r contains a comma *not* '
                           'followed by a space')
            ]:
                assert not re.search(r, rep), (msg % (err, rep))
            if rep.count(','):
                if not rep.endswith(','):
                    assert 'disabled' in rep.split(',')[-1], \
                        ('currently corrections must end with trailing "," (if'
                         ' multiple corrections are available) or '
                         'have "disabled" in the comment')
            reps = [r.strip() for r in rep.lower().split(',')]
            reps = [r for r in reps if len(r)]
            err_dict[err] = reps
            unique = list()
            for r in reps:
                if r not in unique:
                    unique.append(r)
            assert reps == unique, 'entries are not (lower-case) unique'
    # Loop through warnings here, so we can see them, as we don't get them with recwarn
    #assert len(recwarn) == 0, ('error found %d error entries in the aspell '
    #                           'dictionary' % len(recwarn))
    # check for corrections that are errors (but not self replacements)
    for err in err_dict:
        for r in err_dict[err]:
            assert (r not in err_dict) or (r in err_dict[r]), \
                ('error %s: correction %s is an error itself' % (err, r))
