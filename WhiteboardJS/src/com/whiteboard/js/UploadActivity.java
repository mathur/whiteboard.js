package com.whiteboard.js;

import java.io.File;
import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.mime.content.FileBody;
import org.apache.http.impl.client.DefaultHttpClient;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.whiteboard.js.AndroidMultiPartEntity.ProgressListener;

public class UploadActivity extends Activity {
	// LogCat tag
	private static final String TAG = MainActivity.class.getSimpleName();

	private ProgressBar progressBar;
	private TextView txtPercentage;
	private ImageView imgPreview;
	private Button btnUpload;
	private int picNum;
	long totalSize = 0;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_upload);
		txtPercentage = (TextView) findViewById(R.id.txtPercentage);
		btnUpload = (Button) findViewById(R.id.btnUpload);
		progressBar = (ProgressBar) findViewById(R.id.progressBar);
		imgPreview = (ImageView) findViewById(R.id.imgPreview);
		btnUpload.setEnabled(true);
		
		Intent i = this.getIntent();
		picNum = i.getIntExtra("picNum", 0);
		Log.e(TAG, "picnum=" + picNum);

		btnUpload.setOnClickListener(new View.OnClickListener() {

			@Override
			public void onClick(View v) {
				// uploading the file to server
				new UploadFileToServer(0,picNum).execute();
				
			}
		});

	}

	/**
	 * Displaying captured image on the screen
	 * */
	private void previewMedia(int i) {
		// Checking whether captured media is image
		imgPreview.setVisibility(View.VISIBLE);
		// bimatp factory
		BitmapFactory.Options options = new BitmapFactory.Options();
		// down sizing image as it throws OutOfMemory Exception for larger
		// images
		options.inSampleSize = 8;
		// show the first image
		// TODO: show all the pictures
		Log.e(TAG,"IMAGE NUM"+i);
		final Bitmap bitmap = BitmapFactory
				.decodeFile(MainActivity.folderUri.getPath() + File.separator
						+ "IMG_" + i + ".jpg", options);
		imgPreview.setImageBitmap(bitmap);
	}

	/**
	 * Uploading the file to server
	 * */
	private class UploadFileToServer extends AsyncTask<Void, Integer, String> {

		private int i;

		public UploadFileToServer(int i, int picNum) {
			this.i = i;
		}

		@Override
		protected void onPreExecute() {
			// setting progress bar to zero
			previewMedia(i);
			btnUpload.setEnabled(false);
			progressBar.setProgress(0);
			super.onPreExecute();
		}

		@Override
		protected void onProgressUpdate(Integer... progress) {
			// Making progress bar visible
			progressBar.setVisibility(View.VISIBLE);

			// updating progress bar value
			progressBar.setProgress(progress[0]);

			// updating percentage value
			txtPercentage.setText(String.valueOf(progress[0]) + "%");
		}

		@Override
		protected String doInBackground(Void... params) {
			return uploadFile();
		}

		@SuppressWarnings("deprecation")
		private String uploadFile() {
			String responseString = null;

			HttpClient httpclient = new DefaultHttpClient();
			HttpPost httppost = new HttpPost(Config.FILE_UPLOAD_URL);

			try {
				AndroidMultiPartEntity entity = new AndroidMultiPartEntity(
						new ProgressListener() {

							@Override
							public void transferred(long num) {
								publishProgress((int) ((num / (float) totalSize) * 100));
							}
						});

				// send all files

				File sourceFile = new File(MainActivity.folderUri.getPath()
						+ File.separator + "IMG_" + i + ".jpg");
				Log.e(TAG, "adding image " + sourceFile.getPath());
				entity.addPart("image", new FileBody(sourceFile));

				totalSize = entity.getContentLength();
				httppost.setEntity(entity);

				// Making server call
				HttpResponse response = httpclient.execute(httppost);

				int statusCode = response.getStatusLine().getStatusCode();
				if (statusCode == 200) {
					// Server response
					responseString = "Success!";
				} else {
					responseString = "Error occurred! Http Status Code: "
							+ statusCode;
				}

			} catch (ClientProtocolException e) {
				responseString = e.toString() + " ClientProtocolException";
			} catch (IOException e) {
				responseString = e.toString() + " IOException";
			}
			
			return responseString;

		}

		@Override
		protected void onPostExecute(String result) {
			Log.e(TAG, "Response from server: " + result);
			// showing the server response in an alert dialog
			
			//run on last image
			if (i==picNum){
				showAlert(result);
				// delete the image files
				File imageDirectory = new File(MainActivity.folderUri.getPath());
				String[] images = imageDirectory.list();
				for (int i=0;i<images.length;i++){
					File img = new File(images[i]);
					img.delete();				
				}
			}		
			else {
				new UploadFileToServer(++i,picNum).execute();
			}
			super.onPostExecute(result);
			
		}

	}

	/**
	 * Method to show alert dialog
	 * */
	private void showAlert(String message) {
		message += "\n"
				+ "You will receive an email shortly with your new website!";

		AlertDialog.Builder builder = new AlertDialog.Builder(this);
		builder.setMessage(message).setTitle("Response from Servers")
				.setCancelable(false)
				.setPositiveButton("OK", new DialogInterface.OnClickListener() {
					public void onClick(DialogInterface dialog, int id) {
						// do nothing
					}
				});
		AlertDialog alert = builder.create();
		alert.show();
	}

}
