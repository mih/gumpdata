siftnfix_mag_phase () {
  # directory with the dicoms
  dcmdir=$1
  # series number to work with
  series=$2
  # get the relevant dicoms out
  mkdir -p "fm_${series}_phase"
  mkdir -p "fm_${series}_mag"
  echo "START: scanning for fieldmap DICOMs"
  for i in $dcmdir/*; do
    # ignore any image that is not part of the requested series
    [ "$(get_series_nmbr $i)" != "$series" ] && continue
    # what kind of image is it?
    magphase="$(get_mag_vs_phase $i)"
    # magnitude
    if [ "$magphase" = 'M' ]; then ln -fs ../$i "fm_${series}_mag/"
    # phase
    elif [ "$magphase" = 'P' -o "$magphase" = 'B0' ]; then
      ln -fs ../$i "fm_${series}_phase/"
      # 
      ss="$(get_scale_slope $i)"
      rs="$(get_rescale_slope $i)"
      ri="$(get_rescale_intercept $i)"
      # full rescale to FP, need to push the proper values into the right
      # DICOM tags -- just following the Philips docs
      dcmodify -i "(0028,1052)=$(echo "scale=10; $ri/($rs * $ss)" | bc)" \
               -i "(0028,1053)=$(echo "scale=10; 1.0/$ss" | bc)" \
               $i 2> /dev/null
      rm -f "$i".bak*
#      # partial rescale to DV
#      #dcmodify -i "(0028,1052)=$ri" -i "(0028,1053)=$rs" $i 2> /dev/null
    else echo "WARN: neither magn nor phase image (maybe RAW?)"
    fi
  done
  echo "DONE: scanning for fieldmap DICOMs"
}

get_series_nmbr () {
  dcmdump -s +L +M $1 +P '0020,0011' | sed -e "/\[/s/.*\[\(.*\)\]/\1/" -e 's/[ ]*#.*//g'
}

get_mag_vs_phase () {
  dcmdump -s +L +M $1 +P '2005,1011' | sed -e "/\[/s/.*\[\(.*\)\]/\1/" -e 's/[ ]*#.*//g'
}

get_scale_slope () {
  dcmdump -s +L +M $1 +P '2005,100e' | sed -e 's/.*FL //g' -e 's/[ ]*#.*//g'
}

get_rescale_slope () {
  dcmdump -s +L +M $1 +P '2005,140a' | sed -e 's/.*DS \[//g' -e 's/\][ ]*#.*//g'
}

get_rescale_intercept () {
  dcmdump -s +L +M $1 +P '2005,1409' | sed -e 's/.*DS \[//g' -e 's/\][ ]*#.*//g'
}

## fieldmap
convert_fieldmap () {
  dcmdir="$1"
  series="$2"
  wdir="$3"
  initxfm="$4"
  destdir="$5"
  outid="$6"
  convcall="$7"
  niitmpdir="$8"

  siftnfix_mag_phase $dcmdir "$series"
  # magnitude image
  echo "CONVERT fieldmap (series ${series})"
  $convcall "fm_${series}_mag/"
  anon_txt $(find $niitmpdir -name '*field_map*_info.txt' | sort -n | head -n1) $destdir/fieldmap/fieldmap${outid}_mag_dicominfo.txt
  getdeface $(find $niitmpdir -name '*field_map*.nii' | sort -n | head -n1) \
     "$initxfm" ${wdir}/fm_mag 1 0
  export_defaced fm_mag instd $destdir/fieldmap/fieldmap${outid}_mag
  rm -rf $niitmpdir
  # phase image
  $convcall "fm_${series}_phase/"
  anon_txt $(find $niitmpdir -name '*field_map*_info.txt' | sort -n | head -n1) $destdir/fieldmap/fieldmap${outid}_pha_dicominfo.txt
  getdeface $(find $niitmpdir -name '*field_map*.nii' | sort -n | head -n1) \
     ${wdir}/fm_mag.mat ${wdir}/fm_pha 0 0
  # convert from Hz to rad/sec
  python -c "from numpy import pi; import nibabel as nb; img=nb.load(\"${wdir}/fm_pha_instd.nii\"); data = img.get_data(); data *= 2 * pi; nb.save(img, \"${wdir}/fm_pha_rad.nii.gz\")"
  export_defaced ${wdir}/fm_pha rad $destdir/fieldmap/fieldmap${outid}_pha
  rm -rf $niitmpdir
  echo "DONE fieldmap (series ${series})"
}


