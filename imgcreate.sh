chrootdir=$1
[ -d "$chrootdir" ] || exit 1
size=$(du -b  $chrootdir/ | tail -n 1 | sed "s/\t.*$//g")
size=$(($size+10240000))
dd if=/dev/zero of=filesystem.img bs=$size count=1
mkfs.ext4 filesystem.img
fatfs=$(mktemp)
rm -rf $fatfs
mkdir -p $fatfs
mount filesystem.img $fatfs
cp -rfv $chrootdir/* $fatfs
umount $fatfs
rm -rf $fatfs
