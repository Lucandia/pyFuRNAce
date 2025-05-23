import streamlit as st
import matplotlib.pyplot as plt

### My modules
from utils import check_import_pyfurnace, load_logo, save_origami
check_import_pyfurnace()
import utils.design_functions as des_func
from utils.st_fixed_container import sticky_container


if __name__ == "__main__":
    load_logo()
    ### initiate the session state
    des_func.initiate_session_state()
    st.header('Design', 
              help='Design your RNA nanostructure and '
                    'download it as textfile/python script.')

    ### make the general options for the RNA origami
    des_func.origami_general_options(st.session_state.origami, 
                                     expanded=False)

    cols = st.columns([1.3, 1.3] + [1] * 2 + [2, 1.3], 
                      vertical_alignment='center') 
    with cols[0]:    
        with st.popover("Make a simple origami",
                        use_container_width=False,
                        help='Start by creating a simple origami rather than '
                            'starting from scratch'):
            des_func.simple_origami()

    with cols[2]:
        st.write('OxView 3D colormap:')

    with cols[3]:
        cmap = st.selectbox('OxView 3D colormap:', 
                            ['Reds', None] + plt.colormaps(),
                            key='colormap',
                            label_visibility='collapsed', 
                            help='Change the color of the OxView visualization.')
        st.session_state.oxview_colormap = cmap
    with cols[5]:
        grad = st.toggle('Color gradient path', 
                          key='grad', 
                          help='Toggle the gradient color scheme for the nucleotides')
        st.session_state.gradient = grad


    def motif_menu_expander():
        with st.expander("**Add motifs to the origami:**", expanded=True):
            des_func.make_motif_menu(st.session_state.origami)

    if st.session_state.motif_menu_sticky:
        with sticky_container(mode="top", border=False):
            motif_menu_expander()
            view_opt = des_func.origami_select_display()
    else:
        motif_menu_expander()
        view_opt = des_func.origami_select_display()

    ### select the render mode
    if not st.session_state.origami:
        st.success('The origami is empty, add a motif!')
        st.stop()
    else:
        des_func.origami_build_view(view_opt)

    ### display the dot-bracket notation and sequence constraints 
    # and link to the Generate page

    des_func.display_structure_sequence()

    ### Download the RNA origami structure
    save_origami()

    
    