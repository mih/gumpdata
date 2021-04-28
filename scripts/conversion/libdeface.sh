# where is the de-face mask and template
datadir=${DEFACE_3DMRI_DATA_DIR:-"$(pwd)/gumpdata/data/deface"}

anon_txt () {
  grep -i -v study < $1 | grep -iv subject | grep -iv series > $2
}

export_defaced () {
  # $1 - basename
  # $2 - flavor -> $1_$2
  # $3 - destination
  # $3 - mask destination
  $FSLDIR/bin/fslmaths ${1}_${2} -mul ${1}_defacemask $3 -odt input
  $FSLDIR/bin/imcp ${1}_defacemask ${4}
}

getdeface () {
  # image to deface
  target=$1
  # seed the alignment with an initial transformation
  # make empty string to disable
  init_xfm=$2
  # outfile basename
  out_base=$3
  # flag whether to realign image (1) or use initial transform as such (0)
  update_xfm=$4
  # search radius in degrees
  sr="${5:-90}"
  # bet frac
  bf="${6:-0.5}"

  $FSLDIR/bin/fslreorient2std "${target}" ${out_base}_instd

  if [[ $($FSLDIR/bin/fslinfo ${out_base}_instd | grep '^dim4' | sed -e 's/.* //g') -gt 1 ]]; then
    #echo "Use mean volume as reference for de-facing"
    #$FSLDIR/bin/fslmaths ${out_base}_instd -Tmean ${out_base}_meanvol
    echo "Use first volume as reference for de-facing"
    $FSLDIR/bin/fslroi ${out_base}_instd ${out_base}_meanvol 0 1
  else
    $FSLDIR/bin/imln ${out_base}_instd ${out_base}_meanvol
  fi

  # brain extract
  $FSLDIR/bin/bet ${out_base}_meanvol ${out_base}_brain -R -f "${bf}"

  # subsample highres stuff -- doesn't gain much beyond 1mm resolution
  if [[ $(echo "$(fslinfo ${out_base}_meanvol | grep '^pixdim' | head -n3 | sed -e 's/.* //g' | numbound) > 2.1" | bc) == 1 ]]; then
    imln ${out_base}_brain ${out_base}_subsamp
  else
    echo "Subsample for de-facing"
    $FSLDIR/bin/fslmaths ${out_base}_brain -subsamp2 ${out_base}_subsamp
  fi

  # XXX SOME LIKE IT, SOME NOT
  #opts="-usesqform -bins 256 -cost corratio -searchrx -$sr $sr -searchry -$sr $sr -searchrz -$sr $sr -dof 12"
  opts="-bins 256 -cost corratio -searchrx -$sr $sr -searchry -$sr $sr -searchrz -$sr $sr -dof 12"

  if [ ! -z "$init_xfm" ]; then
    echo "Use given init xfm"
    opts="-init $init_xfm $opts"
  fi

  # align template to input image
  if [ $update_xfm = 1 ]; then
    $FSLDIR/bin/flirt -in $datadir/head_tmpl_brain \
      -inweight $datadir/head_tmpl_weights -ref ${out_base}_subsamp \
      -omat ${out_base}.mat -out ${out_base}_alignedtmpl $opts
    popts="-init ${out_base}.mat"
  else
    if [ ! -z "$init_xfm" ]; then
       ln -s ${init_xfm} ${out_base}.mat
       popts="-init ${out_base}.mat"
    else
       popts=""
    fi
  fi

  # project de-face mask onto reference
  $FSLDIR/bin/flirt -in $datadir/face_teeth_ear_mask -applyxfm \
     $popts -out ${out_base}_defacemask_aligned -interp trilinear \
      -ref ${out_base}_meanvol

  # threshold de-face mask and store as output
  $FSLDIR/bin/fslmaths ${out_base}_defacemask_aligned -thr 0.5 -bin \
     ${out_base}_defacemask -odt char
}
