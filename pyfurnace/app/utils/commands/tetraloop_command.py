import streamlit as st
import pyfurnace as pf
from .motif_command import MotifCommand


class TetraLoopCommand(MotifCommand):
    
    def execute(self, motif=None):
        ### Modify the motif
        if motif:
            seq, flip = self.interface('mod', motif[0].sequence)
            if seq and motif[0].sequence != seq:
                st.session_state.modified_motif_text += f"\nmotif.set_sequence('{seq}')"
                motif.set_sequence(seq)
            elif flip:
                st.session_state.modified_motif_text += f"\nmotif.flip()"
                motif.flip()
            
        ### Create a new motif
        else:
            seq, open_left = self.interface()
            if seq:
                st.session_state.motif_buffer = f"motif = pf.TetraLoop({open_left}, sequence = '{seq}')"
                motif = pf.TetraLoop(open_left, sequence = seq)
            else:
                st.session_state.motif_buffer = f"motif = pf.TetraLoop({open_left})"
                motif = pf.TetraLoop(open_left)
            # save the motif in the session state
            st.session_state.motif = motif
    
    def interface(self, key='', seq_default='UUCG'):
        seq = None
        open_left = False
        col1, col2, col3 = st.columns([1, 1, 4], vertical_alignment='bottom')
        with col1:
            custom_seq = st.toggle("Custom Sequence", key=f'seq_tetra{key}')
        with col2:
            if key == 'mod':
                open_left = st.button('Flip', key=f'open_left_tetra{key}')
            else:
                open_left = st.toggle('Flip', value=st.session_state.current_line_occupied, key=f'open_left_tetra{key}')
        if custom_seq:
            with col3:
                seq = st.text_input('Sequence:', value=seq_default, key=f'txt_seq_tetra{key}')
        return seq, open_left