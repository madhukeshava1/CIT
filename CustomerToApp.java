import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;

import org.apache.commons.codec.binary.Base64;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.util.EntityUtils;
import org.apache.poi.openxml4j.exceptions.InvalidFormatException;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.ss.usermodel.WorkbookFactory;


public class CustToApp 
{
	
	// Declare parameters 
	//forExcel
	BufferedWriter bw = null;
	FileWriter fw = null;
	
	//forTExt
	BufferedWriter bw1 = null;
	FileWriter fw1 = null;
	
	
	
	
	FileInputStream fis = null;
   	Workbook wb = null;
	
	public static void main(String[] args) throws Exception
	{
		String ExcelFilePath ="D:\\Divya\\Clients\\Exotel\\API docs\\Agenttocust_PosScenarios.xls";
		String TextFileName = "Report_CusotmerToApp.txt";
		
		CustToAgent c = new CustToAgent();
		c.openExcelFile(ExcelFilePath);
		c.openFile(TextFileName);
		
		c.getExcelData();
		
		c.closeExcelFile();
		c.closeFile();
    }
	
	
	/*
	 * CallAPI is a program which will make the API call 
	 *  It takes parameters 
	 *  exotelSid
	 *  token
	 *  from
	 *  to 
	 *  exophone
	 *  calltype
	 *  Date Created 1-Nov
	 *  Returns Pass if everty thing is fine , else return exception
	 */
	
	public String CallCustToApp( String exotelSid , String token , String from , String to , String exophone , String calltype , String timeLimit , String timeout_agent , String timeout_user ,String Manfields)
	{
	 HttpClient client = new DefaultHttpClient();
	String authStr = exotelSid + ":" + token;
	
	String url = "https://" + authStr +
	    			 "@twilix.exotel.in/v1/Accounts/" +
	    			 exotelSid + "/Calls/connect";
	
	byte[] authEncBytes = Base64.encodeBase64(authStr.getBytes());
	    String authStringEnc = new String(authEncBytes);
	    HttpPost post = new HttpPost(url);
	    post.setHeader("Authorization", "Basic " + authStringEnc);
	    ArrayList<NameValuePair> nameValuePairs = new ArrayList<NameValuePair>();
        nameValuePairs.add(new BasicNameValuePair("From", from));
	    nameValuePairs.add(new BasicNameValuePair("To", to));
	    nameValuePairs.add(new BasicNameValuePair("CallerId", exophone));
	    nameValuePairs.add(new BasicNameValuePair("CallType", calltype));
	    
	    if ( Manfields.equals("Opt"))
	    {
	    	nameValuePairs.add(new BasicNameValuePair("TimeLimit", timeLimit));
		    nameValuePairs.add(new BasicNameValuePair("Timeout_Agent", timeout_agent));
		    nameValuePairs.add(new BasicNameValuePair("Timeout_User", timeout_user));
	    }
	    else if (Manfields.equals("TimeLimit"))
	    {
	    	nameValuePairs.add(new BasicNameValuePair("TimeLimit", timeLimit));
	    }
	    
	    else if (Manfields.equals("Timeout_Agent"))
	    {
	    	nameValuePairs.add(new BasicNameValuePair("Timeout_Agent", timeout_agent));
	    }
	    else if (Manfields.equals("Timeout_User"))
	    {
	    	nameValuePairs.add(new BasicNameValuePair("Timeout_User", timeout_user));
	    }
	    else if (Manfields.equals("TLTO_User"))
	    {
	    	nameValuePairs.add(new BasicNameValuePair("TimeLimit", timeLimit));
	    	nameValuePairs.add(new BasicNameValuePair("Timeout_User", timeout_user));
	    }
	    else if (Manfields.equals("TLTO_Agent"))
	    {
	    	nameValuePairs.add(new BasicNameValuePair("TimeLimit", timeLimit));
	    	nameValuePairs.add(new BasicNameValuePair("Timeout_Agent", timeout_agent));
	    }
	    else if (Manfields.equals("TO_Agent_User"))
	    {
	    	nameValuePairs.add(new BasicNameValuePair("Timeout_User", timeout_user));
	    	nameValuePairs.add(new BasicNameValuePair("Timeout_Agent", timeout_agent));
	    }
	    
	    
	    try 
	    {
	      post.setEntity(new UrlEncodedFormEntity(nameValuePairs));
	      HttpResponse response = client.execute(post);
           int httpStatusCode = response.getStatusLine().getStatusCode();
           System.out.println(httpStatusCode + " is the status code.");
           HttpEntity entity = response.getEntity();
           String retval = EntityUtils.toString(entity);
           System.out.println(retval);
           
           
           return "httpStatusCode = " + httpStatusCode+ " \nentity =  " + retval;
	    }
	    catch (IOException e) 
	    {
	      e.printStackTrace();
	      return e.getMessage();
	    }
	    
	    //return "Pass";
	}
	    
	    
	
	public void  openExcelFile (String filepath) 
	{

		try 
		{
	    
	 	fis = new FileInputStream(filepath);
	   	wb = WorkbookFactory.create(fis);
		}
		catch (Exception e)
		{
			System.out.println(e.getMessage());
		}
	    
	}

	public void closeExcelFile ()
	{
		try 
		{
		fis.close();
		}
		catch ( Exception e)
		{
			System.out.println(e.getMessage());
		}
	}
	
	public void getExcelData() throws Exception
	    {
			String sheet = "Sheet1";
	    	Sheet s = wb.getSheet(sheet);
	    	int rc = s.getLastRowNum();  //number of rows
	    	String testCaseID , exotelSid , token ,  calltype , timeLimit , timeout_agent , timeout_user ;
	    	String  from , to , exophone, returnMsg , execFlag , Manfields ;
	    	
	    	
	        for(int i=0;i<rc;i++)
	        {
	        	
	        	double tcid ;
	        	
	        	testCaseID = getExcelCellValue(s.getRow(i+1).getCell(0));
	        	exotelSid =getExcelCellValue(s.getRow(i+1).getCell(1));
	            token = getExcelCellValue(s.getRow(i+1).getCell(2));
	            from =  getExcelCellValue(s.getRow(i+1).getCell(3)); //use String.valueOf(object)	          
	            to =  getExcelCellValue(s.getRow(i+1).getCell(4));
	            exophone =  getExcelCellValue(s.getRow(i+1).getCell(5));
	            calltype = getExcelCellValue(s.getRow(i+1).getCell(6));
	            timeLimit = getExcelCellValue(s.getRow(i+1).getCell(7));
	            timeout_agent = getExcelCellValue(s.getRow(i+1).getCell(8));
	            timeout_user = getExcelCellValue(s.getRow(i+1).getCell(9));
	            returnMsg = getExcelCellValue(s.getRow(i+1).getCell(10));
	            execFlag = getExcelCellValue(s.getRow(i+1).getCell(11));
	            Manfields = getExcelCellValue(s.getRow(i+1).getCell(12));
	      
	           
	            if ( !from.equals(""))
	            {
	            	from = from.substring(3);
	            }
	            
	            if ( !to.equals(""))
	            {
	            	to = to.substring(3);
	            }
	            
	            if ( !exophone.equals(""))
	            {
	            	exophone = exophone.substring(3);
	            }
	            
	            
	            printLog("***************Iteration Start*****************"); 
	            printLog("execution flag is : "+  execFlag);
	            printLog("Fields are : "+  Manfields);
	            printLog("testCaseID is : "+ testCaseID);
	            printLog("exotelSid is : "+ exotelSid);
	            printLog("token is : "+ token);
	            printLog("from is : "+ from);
	            printLog("to is : "+ to);
	            printLog("exophone is : "+ exophone);
	            printLog("calltype is : "+  calltype);
	            printLog("TimeLimit is : "+  timeLimit);
	            printLog("TimeOut_Agent is : "+  timeout_agent);
	            printLog("TimeOut_User is : "+  timeout_user);
	            printLog("returnMsg is : "+  returnMsg);
	            
	           //String Yes , No;
	           String returnVal = "";
	           String PassStatus = "";
	           
	         
	           
	           
		        if(execFlag.equals("Yes"))
		        {
		        	 returnVal = CallCustToApp(exotelSid , token , from , to , exophone , calltype , timeLimit , timeout_agent , timeout_user ,Manfields);
		        	 if ( returnVal.contains(returnMsg))
				        {
				        	PassStatus = "Pass";
				        }
				        else
				        {
				        	PassStatus = "Fail";
				        }
		        }
		        else
		        {
		        	PassStatus = "No Run";
		        }
		        
		        
		       //returnVal =	CallAPI(exotelSid , token , from , to , exophone , calltype );
		         printLog(returnVal );
		        printLog("PassStatus is " + PassStatus );
		        printLog("***************Iteration END*****************");
		        
		       
	            
	        }
	        
	      }  
	    
	     

	public String getExcelCellValue(Object myObj)
    {

			String retVal = "";

			if(myObj != null)
			{
				retVal = myObj. toString();
			}

			return retVal ;

    }
	
	
       
        	public void openFile(String fileName) 
        	{
        		try {
        			File file = new File(fileName);
        			if (!file.exists()) 
        			{
        				file.createNewFile();
        			}
        			
        			fw1 = new FileWriter(fileName, true);
        			bw1 = new BufferedWriter(fw1);
        			
        		} 
        		catch (Exception e) 
        		{
        			System.err.println("Unable to open file");
        			e.printStackTrace();
        		}
        	}
        	
        	
        	public void printLog(String message) 
        	{
        		try 
        		{
        			System.out.println(message);		
        				bw1.newLine();
        				bw1.write(message);
        				bw1.flush();
        		} 
        		catch (Exception e) 
        		{
        			System.out.println("Test case failed");
        			e.printStackTrace();
        		}

        	}

        	public void closeFile() 
        	{
        		try 
        		{
        			bw1.close();
        		} 
        		
        		catch (IOException e) 
        		{
        			// TODO Auto-generated catch block
        			e.printStackTrace();
        		}
        	}
}
      
  	