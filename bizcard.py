
import easyocr
from PIL import Image
import numpy as np
import re
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import psycopg2
import io


def image_to_text(path):
    input_image=Image.open(path)
    image_arr= np.array(input_image)
    reader= easyocr.Reader(['en'])
    text= reader.readtext(image_arr,detail= 0)
    return text,input_image


#extracting text from image
def extracted_img_text(texts):
    extracted_text={"NAME":[],"DESIGNATION":[],"COMPANY_NAME":[],"CONTACT":[],"EMAIL":[],
                    "WEBSITE":[],"ADDRESS":[],"PINCODE":[]}
    extracted_text["NAME"].append(texts[0])
    extracted_text["DESIGNATION"].append(texts[1])      

    for i in range(2,len(texts)):
            if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):
                    extracted_text["CONTACT"].append(texts[i])

            elif "@" in texts[i] and ".com" in texts[i]:
                    small =texts[i].lower()
                    extracted_text["EMAIL"].append(small)
            elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
                    small = texts[i].lower()
                    extracted_text["WEBSITE"].append(small)
            elif "Tamil Nadu" in texts[i]  or "TamilNadu" in texts[i] or texts[i].isdigit():
                    extracted_text["PINCODE"].append(texts[i])
            elif re.match(r'^[A-Za-z]',texts[i]):
                    extracted_text["COMPANY_NAME"].append(texts[i])

            else:
                    remove_colon = re.sub(r'[,;]', '', texts[i])
                    extracted_text["ADDRESS"].append(remove_colon)

    for key,value in extracted_text.items():
            if len(value)>0:
                    concatenate = ' '.join(value)
                    extracted_text[key] = [concatenate]
            else:
                    value = 'NA'
                    extracted_text[key] = [value]
    return extracted_text
            

#streamlit part
st.set_page_config(layout= "wide")

st.title("EXTRACTING BUSINESS CARD DATA WITH 'OCR'")
st.write("")


with st.sidebar:
  select= option_menu("Main Menu",["Home", "Upload&Modify", "Delete"])

if select == "Home":
        img1=Image.open(r"C:\Users\Viswa.DP-PC\Desktop\phonepe\maxresdefault.jpg")
        st.image(img1)
        with st.expander("### :red[**BIZCARD :**] "):
                st.write("Bizcard is a python application designed to extract information from business cards")
        with st.expander("### :green[**OCR :**] "):
                oc_img=Image.open(r"C:\Users\Viswa.DP-PC\Desktop\phonepe\0_STfB20RYe10Xwov7.jpg")
                st.image(oc_img)
        
   
            





  

elif select == "Upload&Modify":
    img= st.file_uploader("Upload the Image", type= ["png", "jpg", "jpeg"], label_visibility= "hidden")

    if img is not None:
        st.image(img,width= 300)

        text_image,input_image= image_to_text(img)
        text_dict= extracted_img_text(text_image)

        if text_dict:
            st.success("TEXT IS EXTRACTED SUCCESSFULLY")


        df= pd.DataFrame(text_dict)

    #Converting Image to Bytes
    
        Image_bytes= io.BytesIO()
        input_image.save(Image_bytes,format= "PNG")

        image_data= Image_bytes.getvalue()

        #Creating dictionary
        data= {"Image":[image_data]}
        df_1= pd.DataFrame(data)

        concat_df= pd.concat([df,df_1],axis=1)
        button3= st.button("Save",use_container_width= True)

        if button3:
        
            connection=psycopg2.connect(host="localhost",user="postgres",password="12345",database="biz_card",port="5432")
            mycursor=connection.cursor()
            query="""create table if not exists biz_card(NAME varchar(200),
                                                            DESIGNATION varchar(400),
                                                            COMPANY_NAME varchar(400),
                                                            CONTACT varchar(300),
                                                            EMAIL text,
                                                            WEBSITE text,
                                                            ADDRESS text,
                                                            PINCODE varchar(300))"""
            mycursor.execute(query)
            connection.commit()
            insert_query="""insert into biz_card(NAME,
                                                DESIGNATION,
                                                COMPANY_NAME,
                                                CONTACT,
                                                EMAIL,
                                                WEBSITE,
                                                ADDRESS,
                                                PINCODE
                                                )
                                                    values(%s,%s,%s,%s,%s,%s,%s,%s)"""

            for index,row in concat_df.iterrows():
                values=(row["NAME"],
                        row["DESIGNATION"],
                        row["COMPANY_NAME"],
                        row["CONTACT"],
                        row["EMAIL"],
                        row["WEBSITE"],
                        row["ADDRESS"],
                        row["PINCODE"]
                        )
            mycursor.execute(insert_query,values)
            connection.commit()

            st.success("DATA EXTRACTED TO DB")


    method= st.radio("Select the Option",["None","Preview","Modify"])
    if method == "None":
        st.write("")


    if method == "Preview":

        df= pd.DataFrame(text_dict)

        #Converting Image to Bytes
        Image_bytes= io.BytesIO()
        input_image.save(Image_bytes,format= "PNG")
        image_data= Image_bytes.getvalue()

        #Creating dictionary
        data= {"Image":[image_data]}
        df_1= pd.DataFrame(data)

        concat_df= pd.concat([df,df_1],axis=1)
        st.image(input_image, width = 350)
        st.dataframe(concat_df)

    elif method == "Modify":

    
        df= pd.DataFrame(text_dict)


        #Converting Image to Bytes
        Image_bytes= io.BytesIO()
        input_image.save(Image_bytes,format= "PNG")
        image_data= Image_bytes.getvalue()

        #Creating dictionary
        data= {"Image":[image_data]}
        df_1= pd.DataFrame(data)

        concat_df= pd.concat([df,df_1],axis=1)
        st.image(input_image, width = 350)
        st.dataframe(concat_df)

        connection=psycopg2.connect(host="localhost",user="postgres",password="12345",database="biz_card",port="5432")
        mycursor=connection.cursor()
    
        query= "select * from biz_card"
        mycursor.execute(query)
        
        table = mycursor.fetchall()
        connection.commit()

        df3=pd.DataFrame(table,columns=["NAME","DESIGNATION","COMPANY_NAME","CONTACT","EMAIL",
                                        "WEBSITE","ADDRESS","PINCODE"])

        st.dataframe(df3)

        col1,col2= st.columns(2)
        with col1:
                select_name = st.selectbox("Select the Name",df3["NAME"])
        
        df4 = df3[df3["NAME"]==select_name]
        st.write("")

        col1,col2= st.columns(2)
        with col1:
                modify_name= st.text_input("NAME", df4["NAME"].unique()[0])
                modify_designation= st.text_input("DESIGNATION", df4["DESIGNATION"].unique()[0])
                modify_company= st.text_input("COMPANY_NAME", df4["COMPANY_NAME"].unique()[0])
                modify_contact= st.text_input("CONTACT", df4["CONTACT"].unique()[0])

                concat_df["NAME"] = modify_name
                concat_df["DESIGNATION"] = modify_designation
                concat_df["COMPANY_NAME"] = modify_company
                concat_df["CONTACT"] = modify_contact


        with col2:
                modify_email= st.text_input("EMAIL", df4["EMAIL"].unique()[0])
                modify_website= st.text_input("WEBSITE", df4["WEBSITE"].unique()[0])
                modify_address= st.text_input("ADDRESS", df4["ADDRESS"].unique()[0])
                modify_pincode= st.text_input("PINCODE", df4["PINCODE"].unique()[0])

                concat_df["EMAIL"] = modify_email
                concat_df["WEBSITE"] = modify_website
                concat_df["ADDRESS"] = modify_address
                concat_df["PINCODE"] = modify_pincode


        button3= st.button("Modify",use_container_width= True)

        if button3:
                connection=psycopg2.connect(host="localhost",user="postgres",password="12345",database="biz_card",port="5432")
                mycursor=connection.cursor()

                
                mycursor.execute(f"UPDATE biz_card SET NAME= '{select_name}' WHERE NAME ='{select_name}';")
                connection.commit()

                for index, row in concat_df.iterrows():
                        insert_query = '''INSERT INTO biz_card 
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        '''
                        values= (row['NAME'], row['DESIGNATION'], row['COMPANY_NAME'], row['CONTACT'],
                                row['EMAIL'], row['WEBSITE'], row['ADDRESS'], row['PINCODE'])
                        
                        # Execute the insert query
                        mycursor.execute(insert_query,values)

                        # Commit the changes
                        connection.commit()


                connection=psycopg2.connect(host="localhost",user="postgres",password="12345",database="biz_card",port="5432")
                mycursor=connection.cursor()
                
                query= "select * from biz_card"
                mycursor.execute(query)
                
                table = mycursor.fetchall()
                connection.commit()

                df5= pd.DataFrame(table, columns= ["NAME","DESIGNATION","COMPANY_NAME","CONTACT",
                                                        "EMAIL","WEBSITE","ADDRESS","PINCODE"])

                st.dataframe(df5)

                st.success("MODIFIED SUCCESSFULLY")

if select== "Delete":
        connection=psycopg2.connect(host="localhost",user="postgres",password="12345",database="biz_card",port="5432")
        mycursor=connection.cursor()


        col1,col2= st.columns(2)
        with col1:
                mycursor.execute("SELECT * FROM biz_card")
                connection.commit()
                table1= mycursor.fetchall()


        

        names=[]

        for i in table1:
                names.append(i[0])

        name_select= st.selectbox("Select the Name",options= names)

        with col2:
                mycursor.execute(f"SELECT * FROM biz_card WHERE NAME ='{name_select}'")
                connection.commit()
                table2= mycursor.fetchall()

        df7=pd.DataFrame(table2,columns=["NAME","DESIGNATION","COMPANY_NAME","CONTACT","EMAIL",
                                        "WEBSITE","ADDRESS","PINCODE"])

        st.dataframe(df7)

        if name_select :
                col1,col2,col3= st.columns(3)

        with col1:
                st.write(f"Selected Name : {name_select}")
                st.write("")
                st.write("")

                
        with col2:
                st.write("")
                st.write("")
                st.write("")
                st.write("")
                remove= st.button("Delete",use_container_width= True)

        if remove:
                mycursor.execute(f"DELETE FROM biz_card WHERE NAME ='{name_select}'")
                connection.commit()

                st.warning("DELETED")
        mycursor.execute(f"SELECT * FROM biz_card ")
        connection.commit()
        table3= mycursor.fetchall()

        df8=pd.DataFrame(table3,columns=["NAME","DESIGNATION","COMPANY_NAME","CONTACT","EMAIL",
                                        "WEBSITE","ADDRESS","PINCODE"])

        st.dataframe(df8)