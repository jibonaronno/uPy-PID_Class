
import pyb, micropython
micropython.alloc_emergency_exception_buf(100)

class PidEncoderPwm(object):
	def __init__(self):
		self.prev_error = 0.0
		self.i_Temp = 0.0

		self.Kp = 2.3
		#self.Ki = 0.7
		#self.Kd = 40.3
		self.Ki = 0.05
		self.Kd = 0.01
		self.set_point = 555
		self.PWM_Temp = 166.0
		self.step_count = 1


	def pwm_change(self, new_measured_value, blast_factor = 0):

		err_value = self.set_point - new_measured_value
		P_Term = self.Kp * err_value

		b_fac = 0

		self.i_Temp = self.i_Temp + err_value
		iTemp = self.i_Temp
		self.step_count += 1
		#if(iTemp > 25000):
			#iTemp = 25000
		#elif(iTemp < 8000):
			#iTemp = 8000

		I_Term = (self.Ki * self.i_Temp)

########################################################################
## blast factor is only applicable when blast_factor parameter is applied
		if(blast_factor > 0):
			b_fac = I_Term - ((self.set_point - err_value) * blast_factor)

			if(b_fac > 0):
				I_Term = b_fac
##########################################################################

		D_Term = self.Kd * (self.prev_error - err_value)
		self.prev_error = err_value

		PWM_duty = (P_Term + I_Term) + D_Term
		#print("Sample Text")
		#print("FB:{:04d} ERR:{:d} PT:{:d} IT:{:d} DT:{:d} PWM:{:d}".format(new_measured_value, err_value, int(P_Term), int(I_Term), int(D_Term), int(PWM_duty)))
		print("{:d},{:d},{:d},{:d},{:d},{:d}".format(new_measured_value, err_value, int(P_Term), int(I_Term), int(D_Term), int(PWM_duty)))

		return PWM_duty
