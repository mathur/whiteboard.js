package com.whiteboard.js;

import java.io.File;
import java.util.ArrayList;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;

public class MainActivity extends Activity {

	// LogCat tag
	private static final String TAG = MainActivity.class.getSimpleName();

	// Camera activity request codes
	private static final int CAMERA_CAPTURE_IMAGE_REQUEST_CODE = 100;

	public static final int MEDIA_TYPE_IMAGE = 1;
	private static int picNum = 1; // reset this when upload is made
	private Button btnCapturePicture;
	
	public static Uri folderUri; // file url to image directory

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);

		// Changing action bar background color
		// These two lines are not needed

		btnCapturePicture = (Button) findViewById(R.id.btnCapturePicture);

		/**
		 * Capture image button click event
		 */
		btnCapturePicture.setOnClickListener(new View.OnClickListener() {

			@Override
			public void onClick(View v) {
				// capture picture
				captureImage();
			}
		});

		// Checking camera availability
		if (!isDeviceSupportCamera()) {
			Toast.makeText(getApplicationContext(),
					"Sorry! Your device doesn't support camera",
					Toast.LENGTH_LONG).show();
			// will close the app if the device does't have camera
			finish();
		}
	}

	/**
	 * Checking device has camera hardware or not
	 * */
	private boolean isDeviceSupportCamera() {
		if (getApplicationContext().getPackageManager().hasSystemFeature(
				PackageManager.FEATURE_CAMERA)) {
			// this device has a camera
			return true;
		} else {
			// no camera on this device
			return false;
		}
	}

	/**
	 * Launching camera app to capture image
	 */
	private void captureImage() {
		Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);

		Uri fileUri = getOutputMediaFileUri();
		
		//pass the file name and store the image
		intent.putExtra(MediaStore.EXTRA_OUTPUT, fileUri);

		// start the image capture Intent
		startActivityForResult(intent, CAMERA_CAPTURE_IMAGE_REQUEST_CODE);
	}

	/**
	 * Here we store the file url as it will be null after returning from camera
	 * app
	 */
	@Override
	protected void onSaveInstanceState(Bundle outState) {
		super.onSaveInstanceState(outState);

		// save file url in bundle as it will be null on screen orientation
		// changes
		outState.putParcelable("folder_uri", folderUri);
	}

	@Override
	protected void onRestoreInstanceState(Bundle savedInstanceState) {
		super.onRestoreInstanceState(savedInstanceState);

		// get the file url
		folderUri = savedInstanceState.getParcelable("folder_uri");
	}

	/**
	 * Receiving activity result method will be called after closing the camera
	 * */
	@Override
	protected void onActivityResult(int requestCode, int resultCode, Intent data) {
		// if the result is capturing Image
		if (requestCode == CAMERA_CAPTURE_IMAGE_REQUEST_CODE) {
			if (resultCode == RESULT_OK) {

				// check if the user wants to continue
				DialogInterface.OnClickListener dialogClickListener = new DialogInterface.OnClickListener() {

					public void onClick(DialogInterface paraDialog,
							int paramButton) {
						switch (paramButton) {
						case DialogInterface.BUTTON_POSITIVE:
							// capture another image
							picNum++;
							captureImage();
							break;

						case DialogInterface.BUTTON_NEGATIVE:
							// successfully captured the image
							// launching upload activity
							launchUploadActivity();
							picNum = 1; // reset pic num
							break;
						}
					}
				};

				AlertDialog.Builder builder = new AlertDialog.Builder(this);
				builder.setMessage("Do you want to capture another page?")
						.setPositiveButton("Yes!", dialogClickListener)
						.setNegativeButton("No, I'm done", dialogClickListener)
						.show();

			} else if (resultCode == RESULT_CANCELED) {

				// user cancelled Image capture
				Toast.makeText(getApplicationContext(),
						"User cancelled image capture", Toast.LENGTH_SHORT)
						.show();

			} else {
				// failed to capture image
				Toast.makeText(getApplicationContext(),
						"Sorry! Failed to capture image", Toast.LENGTH_SHORT)
						.show();
			}

		}
	}

	private void launchUploadActivity() {
		Intent i = new Intent(MainActivity.this, UploadActivity.class);
		i.putExtra("picNum", picNum);
		startActivity(i);
	}

	/**
	 * ------------ Helper Methods ----------------------
	 * */

	/**
	 * Creating file uri to store image
	 */
	public Uri getOutputMediaFileUri() {
		return Uri.fromFile(getOutputMediaFile());
	}

	/**
	 * returning image
	 */
	private static File getOutputMediaFile() {

		// External sdcard location
		File mediaStorageDir = new File(
				Environment
						.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES),
				Config.IMAGE_DIRECTORY_NAME);

		// Create the storage directory if it does not exist
		if (!mediaStorageDir.exists()) {
			if (!mediaStorageDir.mkdirs()) {
				Log.d(TAG, "Oops! Failed create " + Config.IMAGE_DIRECTORY_NAME
						+ " directory");
				return null;
			}
		}

		folderUri = Uri.fromFile(mediaStorageDir);
		
		// Create a media file name
		File mediaFile = new File(mediaStorageDir.getPath() + File.separator
					+ "IMG_" + picNum + ".jpg");
		return mediaFile;
	}
}
