package com.whiteboard.js;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.mime.content.FileBody;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.util.EntityUtils;

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
	private String folderPath = null;
	private TextView txtPercentage;
	private ImageView imgPreview;
	private Button btnUpload;
	long totalSize = 0;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_upload);
		txtPercentage = (TextView) findViewById(R.id.txtPercentage);
		btnUpload = (Button) findViewById(R.id.btnUpload);
		progressBar = (ProgressBar) findViewById(R.id.progressBar);
		imgPreview = (ImageView) findViewById(R.id.imgPreview);

		// Receiving the data from previous activity
		Intent i = getIntent();

		// image path that is captured in previous activity
		folderPath = i.getStringExtra("folderPath");

		if (folderPath != null) {
			// Displaying the image on the screen
			previewMedia();
		} else {
			Toast.makeText(getApplicationContext(),
					"Sorry, file path is missing!", Toast.LENGTH_LONG).show();
		}

		btnUpload.setOnClickListener(new View.OnClickListener() {

			@Override
			public void onClick(View v) {
				// uploading the file to server
				new UploadFileToServer().execute();
			}
		});

	}

	/**
	 * Displaying captured image on the screen
	 * */
	private void previewMedia() {
		// Checking whether captured media is image
		imgPreview.setVisibility(View.VISIBLE);
		// bimatp factory
		BitmapFactory.Options options = new BitmapFactory.Options();
		// down sizing image as it throws OutOfMemory Exception for larger
		// images
		options.inSampleSize = 8;
		// show the first image
		// TODO: show all the pictures
		final Bitmap bitmap = BitmapFactory.decodeFile(folderPath
				+ File.separator + "IMG_0.jpg", options);
		imgPreview.setImageBitmap(bitmap);
	}

	/**
	 * Uploading the file to server
	 * */
	private class UploadFileToServer extends AsyncTask<Void, Integer, String> {
		@Override
		protected void onPreExecute() {
			// setting progress bar to zero
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

				// we need an array of files
				ArrayList<File> images = new ArrayList<File>();
				for (int i = 0; i < images.size(); i++) {
					// Adding file data to http body
					String imagePath = folderPath + File.separator + "IMG_" + i
							+ ".jpg";
					Log.e(TAG,"adding image "+imagePath);
					File sourceFile = new File(imagePath);
					//entity.addPart("IMG_" + i, new FileBody(sourceFile));
				}
				
				entity.addPart("image", new FileBody(sourceFile));

				totalSize = entity.getContentLength();
				httppost.setEntity(entity);

				// Making server call
				HttpResponse response = httpclient.execute(httppost);
				HttpEntity r_entity = response.getEntity();

				int statusCode = response.getStatusLine().getStatusCode();
				if (statusCode == 200) {
					// Server response
					responseString = EntityUtils.toString(r_entity);
				} else {
					responseString = "Error occurred! Http Status Code: "
							+ statusCode;
				}

			} catch (ClientProtocolException e) {
				responseString = e.toString()+" ClientProtocolException";
			} catch (IOException e) {
				responseString = e.toString()+" IOException";
			}

			return responseString;

		}

		@Override
		protected void onPostExecute(String result) {
			Log.e(TAG, "Response from server: " + result);

			// showing the server response in an alert dialog
			showAlert(result);

			super.onPostExecute(result);

			// return the user to the main page
			Intent returnToMain = new Intent(UploadActivity.this,
					MainActivity.class);
			startActivity(returnToMain);
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
