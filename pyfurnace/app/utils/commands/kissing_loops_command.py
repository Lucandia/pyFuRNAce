import warnings
import streamlit as st
from streamlit_option_menu import option_menu
from pyfurnace.design.motifs import kissing_loops
from .motif_command import MotifCommand
from .. import second_menu_style
from ..motifs_icons import MOTIF_ICONS

kl_name_map = { 'Dimer': "KissingDimer",
                '180°' :"KissingLoop180",
                'Dimer 120°': "KissingDimer120",
                '120°': "KissingLoop120",
                'Branched Dimer': "BranchedDimer",
                'Branched KL': 'BranchedKissingLoop',
            }

class KissingLoopsCommand(MotifCommand):
    
    def execute(self, motif=None):
        warnings.filterwarnings("ignore") # ignore kl energy warning
        ### Modify motif
        if motif:
            flip, seq, energy, tolerance, pk_index = self.interface('mod', motif.get_kissing_sequence(), motif.energy, motif.energy_tolerance, motif.pk_index)
            if flip:
                st.session_state.modified_motif_text += f"\nmotif.flip()"
                motif.flip()
            if seq and motif.get_kissing_sequence() != seq:
                st.session_state.modified_motif_text += f"\nmotif.set_sequence('{seq}')"
                motif.set_sequence(seq)
            if energy and energy != motif.energy:
                st.session_state.modified_motif_text += f"\nmotif.energy = {energy}"
                motif.energy = energy
            if tolerance and tolerance != motif.energy_tolerance:
                st.session_state.modified_motif_text += f"\nmotif.energy_tolerance = {tolerance}"
                motif.energy_tolerance = tolerance
            if pk_index and pk_index != motif.pk_index:
                st.session_state.modified_motif_text += f'\nmotif.pk_index = "{pk_index}"'
                motif.pk_index = pk_index
        ### Create new motif
        else:
            kl_selction = option_menu(None,
                                      list(kl_name_map.keys()),
                                      icons=[MOTIF_ICONS[kl_name_map[name]] for name in kl_name_map],
                                      menu_icon="cast",
                                      orientation="horizontal",
                                      styles=second_menu_style,
                                      key='KLOption',
                                      )
            name = kl_name_map[kl_selction]
            kl_class = getattr(kissing_loops, name)
            flip, top_seq, kl_energy, tolerance, pk_index = self.interface(flip=st.session_state.current_line_occupied and 'Dimer' not in name)
            if top_seq:
                motif = kl_class(open_left = flip, sequence = top_seq)
                st.session_state.motif_buffer = f"motif = pf.{name}(open_left = {flip}, sequence = '{top_seq}')"
            else:
                st.session_state.motif_buffer = f'motif = pf.{name}(open_left = {flip}, energy = {kl_energy}, energy_tolerance = {tolerance}, pk_index = "{pk_index}")'
                motif = kl_class(open_left = flip, energy = kl_energy, energy_tolerance = tolerance, pk_index = pk_index)
            # save the motif in the session state
            st.session_state.motif = motif
        
        # reset the warning filter
        warnings.filterwarnings("default")

    def interface(self, key='', top_seq=None, kl_energy=-8.5, energy_tolerance=0.5, default_pk_index=None, flip=False):
        def pk_index_interface():
            all_pk_indexes = ['0']
            last_ind = 0
            for last_ind in range(1, st.session_state.max_pk_index):
                all_pk_indexes.append(str(last_ind))
                all_pk_indexes.append(str(last_ind) + "'")
            all_pk_indexes.append(str(last_ind + 1))
            if default_pk_index is not None:
                index_for_list = all_pk_indexes.index(default_pk_index)
            else:
                index_for_list = len(all_pk_indexes) - 1
            pk_index = st.selectbox('Pseudoknot id:', 
                                    options=all_pk_indexes, 
                                    index=index_for_list, 
                                    key=f'pk_index_kl{key}',
                                    help="Select the pseudoknot id for the kissing loop motif. "
                                    "The id is used to identify the pseudoknot in the sequence."
                                    " Pseudoknots with the same id will have the same sequence."
                                    " Pseudoknots with the same id, but with a quote \"'\""
                                    " will have a complementary sequence. Pseudoknots with id 0"
                                    " will not pair with any other pseudoknot."
                                    )
            return pk_index

        col1, col2, col3 = st.columns([1, 1, 5], vertical_alignment='bottom')
        open_left = False
        with col1:
            specific_seq = st.toggle("Custom Sequence", key=f'seq_int_kl{key}')
        with col2:
            if key == 'mod':
                open_left = st.button('Flip', key=f'open_left_kl{key}')
            else:
                open_left = st.toggle('Flip', value=flip, key=f'open_left_kl{key}')
        with col3:
            if specific_seq:
                subcol1, subcol2 = st.columns([5, 1])
                with subcol1: # either sequence of energy info
                    top_seq = st.text_input('Sequence:', key=f'seq_top_int_kl{key}', value=top_seq)
                with subcol2:
                    pk_index = pk_index_interface()
            else:
                subcol1, subcol2  = st.columns([4, 1])
                min_kl_E = abs(kl_energy) - abs(energy_tolerance)
                max_kl_E = abs(kl_energy) + abs(energy_tolerance)
                with subcol1:
                    kl_range = st.slider('Kissing binding energy range:', 
                                                  min_value=2.0, 
                                                  max_value=15.0, 
                                                  value=(min_kl_E, max_kl_E),  
                                                  step=0.1, 
                                                  format='-%.1f', 
                                                  key=f'energy_range_kl{key}')
                    kl_energy = round(- sum(kl_range) / 2, 2)
                    energy_tolerance = round(abs(kl_range[1] - kl_range[0]) / 2, 3) 
                with subcol2:
                    pk_index = pk_index_interface()


        return open_left, top_seq, kl_energy, energy_tolerance, pk_index
