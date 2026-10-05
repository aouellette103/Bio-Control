import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator


class BioprocessMonitor:
    def __init__(self, filepath, ph_lims, temperature_lims):
        self.filepath=filepath
        self.ph_min=ph_lims[0]
        self.ph_max=ph_lims[1]
        self.temperature_min=temperature_lims[0]
        self.temperature_max=temperature_lims[1]

    def extract_batch(self, batch_id):
        df = pd.read_csv(self.filepath)
        return df.loc[:,"batch_id"]==batch_id


    def optimal_ph_mask(self, df_batch):
        ph_high=self.ph_max
        ph_low=self.ph_min
        mask_ph_high=df_batch["pH"]<=ph_high
        mask_ph_low=df_batch["pH"]>=ph_low
        mask_ph=mask_ph_high & mask_ph_low
        return mask_ph


    def optimal_temperature_mask(self, df_batch):
        temp_high=self.temperature_max
        temp_low=self.temperature_min
        mask_temp_high=df_batch["temperature_C"]<=temp_high
        mask_temp_low=df_batch["temperature_C"]>=temp_low
        mask_temp=mask_temp_high & mask_temp_low
        return mask_temp

    def get_n_batches(self):
        df=pd.read_csv(self.filepath)
        return df["batch_id"].nunique()

    def export_dashboard(self, batch_id, filepath):
        df=pd.read_csv(self.filepath)

        df_batch=df[df.batch_id==batch_id]
        fig,axs=plt.subplots(2,2,figsize=(12,10),dpi=200,layout="constrained")
        ax_top_left=axs[0,0]
        ax_top_right=axs[0,1]
        ax_bottom_left=axs[1,0]
        ax_bottom_right=axs[1,1]
        ax_top_left.scatter(df_batch.loc[:,'time_h'], df_batch.loc[:,'C_glucose_g_L^-1'], color='tab:blue', marker='o', s=30, alpha=0.7, edgecolors="black",linewidth=0.5, label='Glucose')
        ax_top_left.scatter(df_batch.loc[:,'time_h'], df_batch.loc[:,'C_biomass_g_L^-1'], color='tab:orange', marker='^', s=30, alpha=0.7, edgecolors="black",linewidth=0.5, label='Biomass')
        ax_top_left.scatter(df_batch.loc[:,'time_h'], df_batch.loc[:,'C_product_g_L^-1'], color='tab:green', marker='s', s=30, alpha=0.7, edgecolors="black",linewidth=0.5, label='Product')
        ax_top_left.set_xlabel("Time [h]")
        ax_top_left.set_ylabel("Concentration [g/L]")
        ax_top_left.legend(loc='upper right')

        temp_in_range = self.optimal_temperature_mask(df_batch)

        # Green circles for valid ranges
        ax_top_right.scatter(df_batch.loc[temp_in_range, 'time_h'], df_batch.loc[temp_in_range, 'temperature_C'],
                             color='green', marker='o', s=30, alpha=0.7, edgecolors="black",linewidth=0.5, label='Optimal')
        # Red X markers for out of bounds
        ax_top_right.scatter(df_batch.loc[~temp_in_range, 'time_h'], df_batch.loc[~temp_in_range, 'temperature_C'],
                             color='red', marker='X', s=30, alpha=0.7, edgecolors="black",linewidth=0.5, label='Sub-Optimal')

        ax_top_right.set_xlabel('Time [h]')
        ax_top_right.set_ylabel('Temperature [°C]')
        ax_top_right.legend(loc='upper right')

        ph_in_range = self.optimal_ph_mask(df_batch)

        # Green circles for valid ranges
        ax_bottom_left.scatter(df_batch.loc[ph_in_range, 'time_h'], df_batch.loc[ph_in_range, 'pH'],
                             color='green', marker='o', s=30, alpha=0.7, edgecolors="black",linewidth=0.5, label='Optimal')
        # Red X markers for out of bounds
        ax_bottom_left.scatter(df_batch.loc[~ph_in_range, 'time_h'], df_batch.loc[~ph_in_range, 'pH'],
                             color='red', marker='X', s=30, alpha=0.7, edgecolors="black",linewidth=0.5, label='Sub-Optimal')

        ax_bottom_left.set_xlabel('Time [h]')
        ax_bottom_left.set_ylabel('pH')
        ax_bottom_left.legend(loc='upper right')


        ax_bottom_right.scatter(df_batch.loc[:, 'time_h'], df_batch.loc[:, 'DO_percent'], color='tab:blue', marker='o', s=30, alpha=0.7, edgecolors="black",linewidth=0.5)
        ax_bottom_right.set_xlabel("Time [h]")
        ax_bottom_right.set_ylabel("Dissolved Oxygen (DO) [%]")

        for ax in axs.flat:
            ax.xaxis.set_major_locator(MultipleLocator(6))

        fig.savefig(filepath)
        plt.close(fig)

    def export_summary(self, filepath):
        summary_data=[]
        df=pd.read_csv(self.filepath)
        for batch_id in range(1,self.get_n_batches()+1):
            df_batch=df[df['batch_id'] == batch_id]
            ph_mask=self.optimal_ph_mask(df_batch)
            ph_optimal_percent=round((ph_mask.sum()/len(df_batch))*100,2)
            temp_mask = self.optimal_temperature_mask(df_batch)
            temp_optimal_percent = round((temp_mask.sum() / len(df_batch)) * 100, 2)
            final_concentration=df_batch['C_product_g_L^-1'].iloc[-1]
            summary_data.append({
                "batch_id": batch_id,
                "ph_optimal_percent": ph_optimal_percent,
                "temperature_optimal_percent": temp_optimal_percent,
                "Final_C_product_g_L^-1": final_concentration
            })
        column_names=["batch_id","ph_optimal_percent","temperature_optimal_percent","Final_C_product_g_L^-1"]
        df_export=pd.DataFrame(summary_data,columns=column_names)
        df_export.to_csv(filepath, index=False)
        return df_export