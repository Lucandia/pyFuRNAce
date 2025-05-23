from typing import Optional
import numpy as np
from ..core.symbols import *
from ..core.coordinates_3d import Coords
from ..core.sequence import Sequence
from ..core.strand import Strand
from .stem import Stem

### DAE PARALLEL FROM PDB MEAN roughly refined
# DAE_T_53 = np.array([[-0.79306138, -0.05738916, -0.60643229, -0.60152068],
#                     [-0.05738916, -0.98408458,  0.16817856, -0.26217635],
#                     [-0.60643229,  0.16817856,  0.77714596, -0.83494375],
#                     [ 0.        ,  0.        ,  0.        ,  1.        ],])

# DAE_T_35[[-0.79306138, -0.05738916, -0.60643229, -0.99842575],
#                     [-0.05738916, -0.98408458,  0.16817856, -0.15210483],
#                     [-0.60643229,  0.16817856,  0.77714596,  0.32818404],
#                     [ 0.        ,  0.        ,  0.        ,  1.        ],])

### DAE PARALLEL FROM PDB MEAN refined for ss-assembly
DAE_T_53 = np.array([[-0.82936192, -0.04732277, -0.55670411, -0.60615603],
                     [-0.0473231 , -0.98687633,  0.15438835, -0.23843062],
                     [-0.55670399,  0.15438806,  0.81623819, -0.84790395],
                     [ 0.        ,  0.        ,  0.        ,  1.        ],])
DAE_T_35 = np.array([[-0.82936221, -0.04732235, -0.55670361, -0.98603719],
                     [-0.04732238, -0.98687625,  0.15438865, -0.13307951],
                     [-0.55670361,  0.15438867,  0.81623846,  0.39145356],
                     [ 0.        ,  0.        ,  0.        ,  1.        ],])

class Dovetail(Stem):
    def __init__(self,
                 length: int = 0,
                 sequence: str = '',
                 up_cross: bool = True,
                 down_cross: bool = True,
                 sign: int = 1,
                 wobble_interval: int = 5,
                 wobble_tolerance: int = 2,
                 wobble_insert: str = "middle",
                 strong_bases: Optional[bool] = None,
                 **kwargs
                 ) -> None:
        """
        Initialize a Dovetail motif, which is a helical stem with configurable 
        entry/exit junctions.

        Parameters
        ----------
        length : int, default=0
            Number of nucleotides in the stem. Sign determines dovetail direction
        sequence : str, default=''
            Sequence of the stem. Overrides length if provided.
        up_cross : bool, default=True
            Whether to include a top crossover motif.
        down_cross : bool, default=True
            Whether to include a bottom crossover motif.
        sign : int, default=1
            Direction of dovetail: +1 (right), -1 (left).
        wobble_interval : int, default=5
            Interval between wobble base pairs (default is 5).
        wobble_tolerance : int, default=2
            Random deviation for wobble interval (default is 2).
        wobble_insert : str, default="middle"
            Position of wobble insertion: "middle", "start", or "end".
        strong_bases : bool, optional
            If True, use strong base pairing; if None strong bases are set only if 
            `up_cross` and `down_cross` are both True.
        **kwargs : dict
            Additional keyword arguments passed to `Stem`.

        Raises
        ------
        ValueError
            If `length` is not an integer.
        """
        if not isinstance(length, int):
            raise ValueError("The length parameter must be an integer.")
        
        # initialize the attributes
        self._up_cross = bool(up_cross)
        self._down_cross = bool(down_cross)
        if sequence:
            if sign < 0:
                self._sign = -1
            else:
                self._sign = +1
        else:
            self._sign = +1 if length >= 0 else -1

        kwargs['join'] = False
        super().__init__(length=length, 
                         sequence=sequence, 
                         wobble_interval=wobble_interval, 
                         wobble_tolerance=wobble_tolerance, 
                         wobble_insert=wobble_insert,
                         strong_bases=strong_bases,
                        **kwargs)

    ### 
    ### PROPERTIES
    ###

    @property
    def up_cross(self):
        """Returns boolian describing wether the dovetail has a top crossing"""
        return self._up_cross
    
    @up_cross.setter
    def up_cross(self, new_bool):
        """ Set boolian describing wether the dovetail has a top crossing"""
        self._up_cross = bool(new_bool)
        self.length = self._length

    @property
    def down_cross(self):
        """Returns boolian describing wether the dovetail has a bottom crossing"""
        return self._down_cross
    
    @down_cross.setter
    def down_cross(self, new_bool):
        """Set boolian describing wether the dovetail has a bottom crossing"""
        self._down_cross = bool(new_bool)
        self.length = self._length

    def set_top_sequence(self, new_seq, sign = 0):
        """ Set the sequence of the top strand """
        if not isinstance(new_seq, (str, Sequence)):
            raise TypeError(f'The sequence of a stem must be a string, got {new_seq}.')
        if sign not in [-1, 0, 1]:
            raise ValueError(f'The sign of the dovetail must be -1, 0 or 1, got {sign}.')
        self._sign = sign
        if not sign:
            if self._length >= 0:
                self._sign = +1
            else:
                self._sign = -1
            
        self._length = len(new_seq) * self._sign
        self._create_strands(sequence=new_seq)

    def set_bottom_sequence(self, new_seq, sign = None):
        """ Set the sequence of the bottom strand """
        self.set_top_sequence(sequence=new_seq.translate(nucl_to_pair)[::-1], sign=sign)

    ###
    ### Protected METHODS
    ###

    def _create_strands(self,
                        sequence: Optional[str] = None,
                        length: int = 0,
                        return_strands: bool = False,
                        **kwargs
                        ) -> Optional[List[Strand]]:
        """
        Internal method to generate top and bottom strands with dovetail crossover features.

        Parameters
        ----------
        sequence : str, optional
            Sequence to assign to the top strand. If None, generated based on length.
        length : int, optional
            Length of the stem (used if `sequence` is None).
        return_strands : bool, optional
            If True, return the strands instead of assigning them (default is False).
        **kwargs : dict
            Additional arguments for strand creation (e.g., `strong_bases`).

        Returns
        -------
        list of Strand or None
            The created strands if `return_strands` is True, otherwise None.
        """
        # select the direction of the dovetail
        if sequence:
            pos = True if self._sign >= 0 else False
            seq_len = len(sequence)
        else:
            pos = True if length >= 0 else False
            seq_len = abs(length)
            self._sign = +1 if pos else -1

        up_cross = self._up_cross
        down_cross = self._down_cross

        if kwargs.get('strong_bases') is None:
            kwargs['strong_bases'] =  up_cross and down_cross
        ### Create the top and bottom strands (according to wobble_insert and wobble_interval)
        top_strand, bot_strand = super()._create_strands(sequence=sequence, 
                                                         length=length, 
                                                         compute_coords=False, 
                                                         return_strands=True, 
                                                         **kwargs)

        ### Positive dovetail
        if pos:
            ### Top strands
            top_strand.strand = '──' + top_strand.strand + '╯' * up_cross + '─' * (not up_cross)
            top_strand1 = top_strand
            top_strand2 = Strand('╰' * up_cross + '─' * (not up_cross), 
                                 start=(top_strand1.end[0] + 1, 0), 
                                 direction=(int(not up_cross), int(up_cross)))

            ### Bottom strands
            bot_strand1 = Strand('╮' * down_cross + '─' * (not down_cross), start=(0, 2), direction=(-int(not down_cross), - int(down_cross)))
            # adjust the stem start position, strand and direction
            bot_strand.strand = '──' + bot_strand.strand + '╭' * down_cross + '─' * (not down_cross)
            bot_strand.start = (bot_strand.start[0] + 4, 2)
            bot_strand.direction = (-1, 0)
            bot_strand2 = bot_strand

        ### Negative dovetail
        else:
            ### Top strands
            top_strand1 = Strand('╯' * up_cross + '─' * (not up_cross), start=(0, 0), direction=(1, 0))
            # adjust the stem start position, strand and direction
            top_strand.strand = '╰' * up_cross + '─' * (not up_cross) + top_strand.strand + '──'
            top_strand.start = (1, 0)
            top_strand.direction = (int(not up_cross), int(up_cross))
            top_strand2 = top_strand

            ### Bottom strands
            bot_strand.strand = '╮' * down_cross + '─' * (not down_cross) + bot_strand.strand + '──'
            bot_strand.start = (bot_strand.start[0] + 3, 2)
            bot_strand.direction = (- int(not down_cross), - int(down_cross))
            bot_strand1 = bot_strand
            bot_strand2 = Strand('─' * (not down_cross) + '╭' * down_cross, start=(bot_strand1.start[0] + 1, 2), direction=(-1, 0))

        ### set up the coordinates
        coords = Coords.compute_helix_from_nucl((0,0,0), # start position
                                            (1,0,0), # base vector
                                            (0,1,0), # normal vector
                                            length= seq_len + 2, # length of the helix + dummy ends
                                            double = True)
        # leave out the first and last nucleotide to add the dummy ends
        # Here a schematic of the coordinates indexes:
        #   top_strand1; top_strand2
        #        |           |
        #        0; seq_len;  seq_len + 1;
        #        |        |  |
        #       -N--NNNNNNN--N->
        #        :  :::::::  :
        #      <-N--NNNNNNN--N-
        #        |           |
        #  seq_len * 2 + 3;  seq_len + 2
        #        |           |
        #   bot_strand1; bot_strand2


        if pos: ### the dovetail is positive
            # top strand 1
            top_coord1 = Coords(coords[1: seq_len + 1])
            if up_cross:
                top_coord1.dummy_ends = (coords[0],  # necessary dummy for 0 DT
                                         np.array(Coords.apply_transformation(DAE_T_53, coords[seq_len][0], coords[seq_len][1], coords[seq_len][2], local=True)))
            # top strand 2
            top_coord2 = Coords(np.array(()))
            if up_cross:
                top_coord2.dummy_ends = (np.array(Coords.apply_transformation(DAE_T_35, coords[seq_len + 1][0], coords[seq_len + 1][1], coords[seq_len + 1][2], local=True)),
                                         coords[seq_len + 1])
            # bot strand 1
            bot_coord1 = Coords(np.array(()))
            if down_cross:
                bot_coord1.dummy_ends = (np.array(Coords.apply_transformation(DAE_T_35, coords[-1][0], coords[-1][1], coords[-1][2], local=True)),
                                         coords[-1])
            # bot strand 2
            bot_coord2 = Coords(coords[seq_len + 3: seq_len * 2 + 3])
            if down_cross:
                bot_coord2.dummy_ends = (coords[seq_len + 2], # necessary dummy for 0 DT
                                         np.array(Coords.apply_transformation(DAE_T_53, coords[-2][0], coords[-2][1], coords[-2][2], local=True)))
        else: ### the dovetail is negative
            # top strand 1
            top_coord1 = Coords(np.array(()))
            if up_cross:
                top_coord1.dummy_ends = (coords[0],
                                         np.array(Coords.apply_transformation(DAE_T_53, coords[0][0], coords[0][1], coords[0][2], local=True)))
            # top strand 2
            top_coord2 = Coords(coords[1: seq_len + 1])
            if up_cross:
                top_coord2.dummy_ends = (np.array(Coords.apply_transformation(DAE_T_35, coords[1][0], coords[1][1], coords[1][2], local=True)),
                                         coords[seq_len + 1]) # coords[seq_len + 1], useful for Origami ss_assembly
            # bot strand 1
            bot_coord1 = Coords(coords[seq_len + 3: -1])
            if down_cross:
                bot_coord1.dummy_ends = (np.array(Coords.apply_transformation(DAE_T_35, coords[seq_len + 3][0], coords[seq_len + 3][1], coords[seq_len + 3][2], local=True)),
                                         coords[-1]) #coords[-1], useful for Origami ss_assembly
                
            # bot strand 2
            bot_coord2 = Coords(np.array(()))
            if down_cross:
                bot_coord2.dummy_ends = (np.array(coords[seq_len + 2]),
                                         np.array(Coords.apply_transformation(DAE_T_53, coords[seq_len + 2][0], coords[seq_len + 2][1], coords[seq_len + 2][2], local=True)))

        top_strand1._coords = top_coord1
        top_strand2._coords = top_coord2
        bot_strand2._coords = bot_coord2
        bot_strand1._coords = bot_coord1

        if return_strands:
            return self.join_strands([top_strand1, top_strand2, bot_strand1, bot_strand2])

        self.replace_all_strands([top_strand1, top_strand2, bot_strand1, bot_strand2], 
                                 copy=False, 
                                 join=True)
