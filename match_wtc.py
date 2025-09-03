# import libraries
import os
import parangonar as pa
import partitura as pt
from tqdm import tqdm
import glob
from partitura.io.exportmatch import save_match
from config import SCORE_PATH, PERFORMANCE_PATH, SAVE_PATH


def main():
    matcher = pa.DualDTWNoteMatcher()
    midi_files = glob.glob(os.path.join(PERFORMANCE_PATH, '**/*.midi'))

    for performance_path in tqdm(midi_files):
        score_path = os.path.join(SCORE_PATH, os.path.basename(performance_path).replace('midi', 'musicxml'))
        score = pt.load_score(filename=score_path)  # xml file
        performance = pt.load_performance_midi(filename=performance_path)

        # sometimes the scores contain multiple parts which are best merged for easier processing
        part = pt.score.merge_parts(score)
        # sometimes scores contain repeats that need to unfolded to make the alignment make sense
        unfolded_part = pt.score.unfold_part_maximal(part)

        score_array = unfolded_part.note_array(include_grace_notes=True)
        performance_array = performance.note_array()

        pred_alignment = matcher(score_array, 
                                performance_array,
                                process_ornaments=True,
                                score_part=unfolded_part) # if a score part is passed, ornaments can be handled seperately

        save_filepath = os.path.join(SAVE_PATH, performance_path.split('/')[-2])
        filename = '{}.match'.format(performance_path.split('/')[-1].split('.')[0])
        os.makedirs(save_filepath, exist_ok=True)
        save_match(
            alignment=pred_alignment,
            performance_data=performance,
            score_data=unfolded_part,
            out=os.path.join(save_filepath, filename),
            assume_unfolded=True,
        )


if __name__ == "__main__":
    main()