function listFiles(sourceDir, targetDir) {
     list = getFileList(sourceDir);
     success = 0;
     for (i=0; i<list.length; i++) {
        if (endsWith(list[i],"root.png")==1){
	    open(sourceDir+list[i]);	
	    run("Skeletonize (2D/3D)");
	    imageName=replace(list[i], "root.png", "");
	    saveAs("PNG", targetDir+imageName+"skel.png");
	    close();
            print(sourceDir+list[i]);
            success = 1;
     	}
     }
     if (!success) {
     	print("No files ending .root.png found.");
     }
}


macro "BatchSkeletonize" {
     	print("Running...");
	setBatchMode(true);
    Directories=getArgument()
    Directories=split(Directories, ":")
	SourceDir=Directories[0]
	TargetDir=Directories[1]
    //SourceDir=getDirectory("Choose a source directory");
	//TargetDir=getDirectory("Choose a target directory");
	listFiles(SourceDir, TargetDir);
	setBatchMode(false);
     	print("Finished.");
}
